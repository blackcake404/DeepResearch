from mcp.server.fastmcp import FastMCP
import requests
from openai import OpenAI
import logging

mcp = FastMCP("search")

base_url = "https://openrouter.ai/api/v1"
api_key = "aaa"
model_name = "deepseek/deepseek-chat-v3.1"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# 创建文件处理器
file_handler = logging.FileHandler('test.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

# Generate search queries according to query
def generate_query(query: str, stream=False):
    prompt = """
        You are an expert research assistant. Given the user's query request, generate up to 5 disinct, precise search queries which would be extremely helpful for gathering comprehensive information on the topic.
        Return only a Python list of strings, for example: ['query1', 'query2', 'query3', 'query4', 'query5'].
    """
    response = client.chat.completions.create(
        model = model_name,
        messages=[
            {"role": "system", "content": "You are a helpful and precise research assistant."},
            {"role": "user", "content": f"As your user, my user query is: {query} \n\n {prompt}"}
        ]
    )
    return response.choices[0].message.content

# Evaluate the query result
def query_useful(query: str, text: str) -> str:
    prompt = """
        You are a critical research evaluator. Given the user's query and the content of the webpage, determine if the contents of webpage contains information are relative and useful for address user's query.
        Respond with exactly only one word: "Yes" if the page is useful, or "No" if it is not useful. Do not include any extra text.
    """
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a strict and concise evaluator of research relevance"},
            {"role": "user", "content": f"User's query: {query} \n\n Webpage Content: {text} \n\n {prompt}"}
        ]
    )
    response = response.choices[0].message.content
    if response:
        answer = response.strip()
        if answer in ["Yes", "No"]:
            return answer
        else:
            if "Yes" in answer and "No" not in answer:
                return "Yes"
            if "No" in answer and "Yes" not in answer:
                return "No"
    return "No"

# Extract useful information from query result
def extract_relevant_context(query: str, search_queries: list, text: str):
    prompt = """
        You are an expert information extractor. Given the user's query, search queries that led to this webpage, and the content of this webpage, extract all information that are relevant to answering the user's query.
        Return only the relevant context as plain text without commentary or explanation
    """
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are an expert in extracting and summarizing relevant information."},
            {"role": "user", "content": f"User's query: {query} \n\n Search queries: {search_queries} \n\n Webpage content: {text} \n\n {prompt}"}
        ]
    )
    response = response.choices[0].message.content
    if response:
        return response.strip()
    return ""

# Determine if further research is needed and generate new research queries if need
def generate_new_search_queries(query: str, search_queries: list, all_contexts) -> list:
    all_contexts = '\n'.join(all_contexts)
    prompt = """
        You are an analytical research assistant. Based on the original user's query, hte search queries performed so far, and the extracted contexts from webpages, determine if further research is needed.
        If further research is needed, provide up to 5 new research queries as a list, for example: ['new query1', 'new query2', 'new query3', 'new query4', 'new query5']. If you believe no further research is needed, respond with exactly .
        Output only a list or the token without any additional text.
    """
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are an expert in extracting and summarizing relevant information."},
            {"role": "user", "content": f"User's query: {query} \n\n Previous search queries: {search_queries} \n\n Extracted relevant contexts: {all_contexts} \n\n {prompt}"}
        ]
    )
    response = response.choices[0].message.content
    if response:
        response = response.strip()
        if response =="":
            return ""
        try:
            new_research_queries = eval(response)
            if isinstance(new_research_queries, list):
                return new_research_queries
            else:
                logger.info(f"LLM did not return a list for new research queries as expected. Response: {response}")
                return []
        except Exception as e:
            logger.error(f"Error in generating new research queries: {e}. Response: {response}")
            return []
    return []

# Get web urls
def web_search(query: str, top_k: int = 3, categories: str = "general") -> str:
    search_api = "aaa"
    search_engine_id = "aaa"
    google_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": search_api,
        "cx": search_engine_id,
        "q": query
    }
    if categories == "images":
        params['searchType'] = "image"
    response = requests.get(google_url, params=params, timeout=60)
    response.raise_for_status()
    google_results = response.json().get("items", [])
    results = []
    for item in google_results:
        if categories == 'general':
            formatted_item = {'url': item.get('link')}
            results.append(formatted_item)
        elif categories == 'images':
            formatted_item = {'img_src': item.get('link')}
            results.append(formatted_item)
    
    links = []
    for result in results[:top_k]:
        links.append(result["url" if categories == "general" else "img_src" if categories == "images" else ""])
    return links
    # links = []
    # response = requests.get(f'http://172.20.8.126:8080/search?format=json&q={query}&time_range=&safesearch=0&categories={categories}', timeout=10)
    # results = response.json()['results']
    # for result in results[:top_k]:
    #     links.append(result['url' if categories == 'general' else 'img_src' if categories == 'images' else ''])
    
    # return links

# Use JINA to extra webpage
def fetch_webpage_text(url):
    JINA_BASE_URL = "https://r.jina.ai/"
    full_url = f"{JINA_BASE_URL}{url}"
    try:
        response = requests.get(full_url, timeout=60)
        if response.status_code == 200:
            return response.text
        else:
            logger.info(f"JINA fetch error for {url}: {response.status_code} - {response.text}")
            return ""
    except Exception as e:
        logger.error(f"Error in fetching webpage with JINA: {e}")
        return ""
    
# Process webs
def process_link(link, query, search_queries):
    logger.info(f"Fetching content from: {link}")
    page_text = fetch_webpage_text(link)
    if not page_text:
        return None
    usefulness = query_useful(query, page_text)
    logger.info(f"Page usefulness for {link}: {usefulness}")
    if usefulness == "Yes":
        context = extract_relevant_context(query, search_queries, page_text)
        if context:
            logger.info(f"Extracted context from {link}: {context}")
            return context
    return None

# Get image description
def get_image_description(img_url):
    response = client.chat.completions.create(
        model="qwen/qwen2.5-vl-32b-instruct",
        messages=[
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": "描述图片内容"
                    },
                    {
                        "type": "image_url", 
                        "image_url": {
                            "url": img_url
                        }
                    }
                ]
            },
            
        ]
    )
    return response.choices[0].message.content

#
@mcp.tool()
def search(query: str) -> str:
    iteration_limit = 3
    iteration = 0
    aggregated_contexts = []
    all_search_queries = []
    
    new_search_queries = eval(generate_query(query))
    all_search_queries.extend(new_search_queries)
    if query not in all_search_queries:
        all_search_queries.append(query)
    while iteration < iteration_limit:
        logger.info(f"\n==== Iteration {iteration + 1} ====")
        iteration_contexts = []
        search_results = [web_search(query) for query in new_search_queries]
        unique_links = {}
        
        for idx, links in enumerate(search_results):
            search_query = new_search_queries[idx]
            for link in links:
                if link not in unique_links:
                    unique_links[link] = search_query
        logger.info(f"Aggregated {len(unique_links)} unique links from this iteration.")

        link_results = [
            process_link(link, query, unique_links[link])
            for link in unique_links
        ]
        
        for res in link_results:
            if res:
                iteration_contexts.append(res)

        if iteration_contexts:
            aggregated_contexts.extend(iteration_contexts)
        else:
            logger.info("No useful contexts found in this iteration.")

        new_search_queries = generate_new_search_queries(query, all_search_queries, aggregated_contexts)
        if new_search_queries == "":
            logger.info("LLM decides no further research is needed.")
            break
        elif new_search_queries:
            logger.info(f"LLM provides new search queries: {new_search_queries}")
            all_search_queries.extend(new_search_queries)
        else:
            logger.info("LLM does not provide any new search queries. End.")
            break

        iteration += 1
    return "\n\n".join(aggregated_contexts)

@mcp.tool()
def get_images(query: str) -> str:  # 修复：返回类型改为str
    logger.info(f"Searching for images for query: {query}")
    img_srcs = web_search(query, top_k=3, categories="images")

    results = []
    for img_src in img_srcs:
        logger.info(f"Fetching image description for: {img_src}")
        description = get_image_description(img_src)
        logger.info(f"Image description for {img_src}: {description}")
        results.append(f"图片链接: {img_src}\n描述: {description}")
    
    return "\n\n".join(results) if results else "未找到相关图片或无法获取图片描述"

if __name__ == "__main__":
    mcp.run()