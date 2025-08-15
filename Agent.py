from datetime import datetime
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from groq import Groq
from typing import Annotated
from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END 
from typing import List, Tuple, Optional
import pandas as pd


load_dotenv()
API_KEY = "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"


class State(TypedDict):
    user_query : str
    response: str

def main():
    client = Groq(
        api_key = API_KEY
    )

    
    def feedback_agent(state: State) ->  State:
        
        topic = state["user_query"]
        
        prompt = f"""You are an AI assistant for "SteamNoodles," a restaurant known for its innovative approach to customer experience. Your persona is a friendly, empathetic, and professional human customer service representative.

                    Your task is to write a short, polite, and context-aware reply to the customer feedback provided below.

                    **Follow these strict instructions:**
                    1.  **Acknowledge Key Points:** Your reply must specifically acknowledge the core subject of the customer's feedback (e.g., the food, the service, or the ambiance).
                    2.  **Match the Tone:**
                        *   For **positive** feedback, respond with warmth and gratitude. Express genuine delight in their good experience.
                        *   For **negative** feedback, respond with sincere empathy and offer an apology. Reassure them their feedback is valuable for improvement.
                        *   For **neutral or mixed** feedback, thank them for their time and address their points in a balanced manner.
                    3.  **Be Concise and Human:** Keep the response to a maximum of two sentences. Use friendly, natural language.
                    4.  **Do Not Announce Your Actions:** Never start your reply with phrases like "Here is the reply," "Here is my response," or similar lead-ins. Directly provide the customer-facing reply.
                    5. **Response to the customers conversations of "hi", "hello" with properly
                    refer to the topic given below
                    {topic}
                    """
                
        # invoke the chat 
        chat_completion = client.chat.completions.create(
            messages = [
                {"role": "user" , "content": prompt }
            ],
            model = "llama3-8b-8192",
            temperature = 0.4
        )
        
        state["response"] = chat_completion.choices[0].message.content
        timestamp = datetime.now()
        with open("feedback.csv","a+") as file:
            input_inventory = f"Date and time: {timestamp} | customer feedback: {topic}\n"
     
            file.write(input_inventory)
        return state
    
    def visualize(data):
        
        
        data = eval(data)
        dates = list(data.keys())
        positive = [data[date]['positive'] for date in dates]
        negative = [data[date]['negative'] for date in dates]   
        neutral = [data[date]['neutral'] for date in dates]
        total = [data[date]['total'] for date in dates]

        x = range(len(dates))
        bar_width = 0.2

        # Plot bars
        plt.bar([i - 1.5*bar_width for i in x], positive, width=bar_width, label='Positive', color='green')
        plt.bar([i - 0.5* bar_width for i in x],negative, width=bar_width, label='Negative', color='red')
        plt.bar([i + 0.5*bar_width for i in x], neutral, width=bar_width, label='Neutral', color='blue')
        plt.bar([i + 1.5*bar_width for i in x], total, width=bar_width, label='Total', color='yellow')

        plt.xticks(x, dates, rotation=45)
        plt.xlabel("Date")
        plt.ylabel("Count")
        plt.title("Sentiment Analysis Over Time")
        plt.legend()
        plt.tight_layout()
        plt.show()
        
    def parse_date_range(user_query: str, client) -> Tuple[pd.Timestamp, pd.Timestamp]:
        prompt = f"""
        Convert the user's date range request into start_date and end_date in YYYY-MM-DD format.
        Only return valid String in this format:
            "Start day to end day" 
        date formatting - "YYYY-MM-DD"
        User request: "{user_query}"
        Today is {datetime.now().strftime("%Y-%m-%d")}
        """
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0
        )
        
        date_data = chat_completion.choices[0].message.content
        return date_data
    def sentiment_visualization_agent(state: State) -> State:
        date_range = state["user_query"]
        history =  df = pd.read_csv('feedback.csv', sep='|')

        print(history)
        prompt = f"""You are a data analyst for SteamNoodles' restaurant.
                    Based on the user's request for a date range, generate a sample summary of sentiment data.
                    **Content:** You do not have access to a real database. **Do not Generate realistic, sample data for the requested period** just memoize previous feedbacks
                    look back to previous history of customer feedback and analyse.
                    For example, if the user asks for "last week" or certain time range you can output in to a dictionary consist of following:
                    *Structure*
                    date : date 
                    positive: num of positive feedbacks 
                    negative: num of negative feedbacks
                    neutral : num of neutral feedbacks
                    total : num of total feedbacks
                    
                    User's Date Range Request: "{date_range}"
                    Use only the ***Feedback history***  {history} to  analysis.
                    If user want a analysis of current dat to a previous day or week just get thw current date : {datetime.now()}
                    **Note that to make sure to give report **only** as a dictionary referring to the following structure**
                    **Don't describe the summary and just give the result**
                    Don't give "Based on the user's request for the last week's user feedback report, I've analyzed the previous customer feedback and generated a summary report. Here's the output:"
                    and This report summarizes the sentiment analysis of customer feedback for the last week (March 13th to March 19th). The dictionary keys represent the dates, and the values provide the number of positive, negative, neutral, and total feedbacks for each date.
                    Don't give the response like ***Here is the summary report for the last week:*** way 
                    """

        chat_completion = client.chat.completions.create(
            messages = [
                {"role": "user" , "content": prompt }
            ],
            model = "llama3-8b-8192",
            temperature = 0.4
        )
        state["response"] = chat_completion.choices[0].message.content 
        print(state["response"])
        visualize(state["response"])
        return state
        
    # --- Define Agents DocString ---
    agent_docs = {
        "feedback_agent": feedback_agent.__doc__,
        "sentiment_visualization_agent": sentiment_visualization_agent.__doc__
    }

    def route_logic(state: State ) ->  Literal["feedback_agent", "sentiment_visualization_agent"]:
        prompt = f"""\n
            Your task is to choose the best agent for the job.
            Here is the user query: {state['user_query']}

            You can choose from the following agents:
            - feedback_agent: {agent_docs['feedback_agent']}
            - sentiment_visualization_agent: {agent_docs['sentiment_visualization_agent']}
            if the user gives a feedback related to the noodles its a "feedback"
            if the user asks a customer feedback analysis or report related to a time range its a "sentiment_visualization"
            you should handle this query on {state['user_query']} Respond with just the agent name.\n
            """
        chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
                    model="llama3-8b-8192",
                    temperature=0                )
        decision = chat_completion.choices[0].message.content.strip().lower()
        print("===The Type of Agent===")
        print(decision)
        return "feedback_agent" if "feedback" in decision else "sentiment_visualization_agent"
    
    def router_agent(state: State ) -> State :

        # the router agent 
        # this agent will decide the route path wether "Feedback Aget"  or "Sentiment Visualization Agent"
        print("===Router Agent===")
        print("Router Agent Works")
        return state
    

    # build the state graph

    builder = StateGraph(State)
    builder.add_node("router_agent", router_agent)
    builder.add_node("feedback_agent", feedback_agent)
    builder.add_node("sentiment_visualization_agent",sentiment_visualization_agent)


    builder.set_entry_point("router_agent")
    builder.add_conditional_edges(
        "router_agent",
        route_logic,
        {
            "feedback_agent": "feedback_agent",
            "sentiment_visualization_agent": "sentiment_visualization_agent"
        }
    )
    
    builder.add_edge("router_agent", END)
    builder.add_edge("router_agent", END)

    graph = builder.compile()
    from IPython.display import Image, display
    with open("graph.png", "wb") as f:
        f.write(graph.get_graph().draw_mermaid_png())
    
    while True:
        user_input = input("\nEnter your query (or type 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break

        initial_state = {"user_query": user_input, "response": "" }
        
        # Invoke the graph with the user's query
        final_state = graph.invoke(initial_state)
    
        # Print the final response from the state
        print("\n === Final Output === ")
        a = final_state.get("response", "No response was generated.")
        print(a)

        

if __name__ == "__main__":
    main()

