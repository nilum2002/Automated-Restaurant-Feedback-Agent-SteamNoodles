from datetime import datetime, timedelta
import time 
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
# enter your API key 
API_KEY = ""


class State(TypedDict):
    user_query : str
    response: str

def main():
    client = Groq(
        api_key = API_KEY
    )

    
    def feedback_agent(state: State) ->  State:
        
        topic = state["user_query"]
        # this is for feedback
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
        # this is for identify the feedback tone
        prompt_tone = f"""You are an AI assistant for SteamNoodles, a restaurant known for its innovative approach to customer experienceIdentify the {topic} and give me only the tone of the feedback 
                    1.  **Match the Tone:**
                        *   For **positive** feedback as Positive
                        *   For **negative** feedback as Negative
                        *   For **neutral ** feedback as Neutral
                    **Crucial Rules:**
                    -   **DO NOT** provide any text, explanation, or conversation.
                    -   **DO NOT** use markdown code blocks (like ```python...```).
                    -   The output must be **only** the string list and nothing else.
                    only give the match tone of the {topic}
        
        
                    """
        # invoke the chat
        chat_completion_feedback = client.chat.completions.create(
            messages = [
                {"role": "user" , "content": prompt }
            ],
            model = "llama3-8b-8192",
            temperature = 0.4
        )
        # invoke tone 
        chat_completion_tone = client.chat.completions.create(
            messages = [
                {"role": "user" , "content": prompt_tone}
            ],
            model = "llama3-8b-8192",
            temperature = 0.4
        )
        
        state["response"] = chat_completion_feedback.choices[0].message.content
        customer_tone = chat_completion_tone.choices[0].message.content
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        with open("feedback.csv","a+") as file:
            input_inventory = f"{timestamp} | {customer_tone} | {topic}\n"
     
            file.write(input_inventory)
        return state
    
    def visualize(date_range):
        if eval(date_range)[0] == "None Range":
            print("***Warning***")
            print("Please Give a date range for customer analysis process")
        else:
            date_range = eval(date_range)
            start_date = date_range[0]
            end_date = date_range[1]
            

            df = pd.read_csv('feedback.csv', sep='|', header=None, names=['Date', 'Tone', 'Feedback'], dtype=str)
            df = df.apply(lambda x: x.str.strip())
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

            df = df.dropna(subset=['Date'])
    
            
            
            mask = (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))
            df_range = df.loc[mask]
            # color=['#4CAF50', '#F44336', '#FFC107']
            daily_counts = df_range.groupby([df_range['Date'].dt.date, 'Tone']).size().unstack(fill_value=0)
            for tone in ["Positive", "Negative", "Neutral"]:
                if tone not in daily_counts.columns:
                    daily_counts[tone] = 0
            if not daily_counts.empty:
                daily_counts["Total"] = daily_counts.sum(axis=1)
                daily_counts = daily_counts.sort_index()

                # Plot
                daily_counts[["Positive", "Negative", "Neutral", "Total"]].plot(
                    kind="bar",
                    figsize=(12, 8),
                    color=["#4CAF50", "#FA1100", "#646265", "#A7FA0D"]
                )
            
            plt.title(f"Customer Feedback from {start_date} to {end_date}")
            plt.xlabel("Date")
            plt.ylabel("Number of Feedbacks")
            plt.xticks(ticks=range(0, len(daily_counts), 5), labels=daily_counts.index[::5], rotation=45)
            plt.show()  

    def sentiment_visualization_agent(state: State) -> State:
        user_prompt = state["user_query"]
        
        today = datetime.today().strftime('%Y-%m-%d')
        prompt = f"""You are a precise, single-purpose date-parsing engine. Your only function is to convert a user's natural language query into a string literal representing a Python list with two date strings: a start date and an end date.

                **Output Requirements:**
                1.  **Format:** The output MUST be a string that looks exactly like a Python list: `['YYYY-MM-DD', 'YYYY-MM-DD']`.
                2.  **Content:** For a query about a single day, the start and end dates must be the same.
                3.  **Reference Date:** Use the current date provided as the reference for all relative queries.

                **Crucial Rules:**
                -   **DO NOT** provide any text, explanation, or conversation.
                -   **DO NOT** use markdown code blocks.
                -   The output must be **only** the string list and nothing else.

                **Current Date for Reference:** {today}

                ---
                **--- EXAMPLES ---**
                You must learn from these patterns and handle similar phrasings.

                **// Single Day Examples**
                User Query: "today"
                Output String: ['{today}', '{today}']

                User Query: "yesterday"
                Output String: ['{(datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")}', '{(datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")}']

                User Query: "August 15, 2025"
                Output String: ['2025-08-15', '2025-08-15']

                **// Week-Based Examples**
                User Query: "last 7 days"
                Output String: ['{(datetime.today() - timedelta(days=6)).strftime("%Y-%m-%d")}', '{today}']

                User Query: "this week"
                Output String: ['{(datetime.today() - timedelta(days=datetime.today().weekday())).strftime("%Y-%m-%d")}', '{today}']

                User Query: "last week"
                Output String: ['{(datetime.today() - timedelta(days=datetime.today().weekday()+7)).strftime("%Y-%m-%d")}', '{(datetime.today() - timedelta(days=datetime.today().weekday()+1)).strftime("%Y-%m-%d")}']

                User Query: "the past two weeks"
                Output String: ['{(datetime.today() - timedelta(days=13)).strftime("%Y-%m-%d")}', '{today}']

                **// Month-Based Examples**
                User Query: "this month"
                Output String: ['{datetime.today().replace(day=1).strftime("%Y-%m-%d")}', '{today}']

                User Query: "last month"
                Output String: ['{(datetime.today().replace(day=1) - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")}', '{(datetime.today().replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")}']

                User Query: "last 30 days"
                Output String: ['{(datetime.today() - timedelta(days=29)).strftime("%Y-%m-%d")}', '{today}']

                User Query: "August 2025"
                Output String: ['2025-08-01', '2025-08-31']

                **// Year-Based Examples**
                User Query: "this year"
                Output String: ['{datetime.today().replace(month=1, day=1).strftime("%Y-%m-%d")}', '{today}']

                User Query: "last year"
                Output String: ['{datetime.today().replace(year=datetime.today().year-1, month=1, day=1).strftime("%Y-%m-%d")}', '{datetime.today().replace(year=datetime.today().year-1, month=12, day=31).strftime("%Y-%m-%d")}']

                User Query: "2024"
                Output String: ['2024-01-01', '2024-12-31']

                **// Specific Range Examples**
                User Query: "from Aug 1 to Aug 10 2025"
                Output String: ['2025-08-01', '2025-08-10']
                ---

                **User Query:** "{user_prompt}"
                **Output String:**
                """

        
        chat_completion = client.chat.completions.create(
            messages = [
                {"role": "user" , "content": prompt }
            ],
            model = "llama3-8b-8192",
            temperature = 0.4
        )
        state["response"] = chat_completion.choices[0].message.content
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
            if the user gives a feedback related to the noodles or related to food and beverages its a "feedback"
            if the user asks a customer feedback analysis or report related to a time range or date range its a "sentiment_visualization"
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
        start_time = time.time()
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
        end_time = time.time()
        print(f"The Execution time is {end_time-start_time} seconds")

        

if __name__ == "__main__":
    main()

