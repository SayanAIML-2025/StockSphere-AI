import streamlit as st
import time
from src.app import run_stocksphere
# from crewaiorchagent.utils.intent import Intent
# from crewaiorchagent.main import kickoff

if 'chat_hist' not in st.session_state:
    st.session_state.chat_hist=[]
if 'chat_init' not in st.session_state:
    st.session_state.chat_init=True


# ############## replace with crewai orchestrator
# def ai_orch(ques,chat_hist):
#     intent_agent=Intent()
#     result=intent_agent.identify_intent(chat_hist)
#     if "Welcome intent" in result:
#         try:
#             result = result.split("\n")[-1]
#             print(result)
#             assistant_message = {"role": "system", "content": result}
#             # assistant_message=f"System: {result}"
#             st.session_state.chat_hist.append(assistant_message)
#             return {
#                 "messages": st.session_state.chat_hist
#             }

#         # except HTTPException as e:
#         except Exception as e:
#             print(f"Error in processing welcome inteent: {e}")
#             assistant_message = {"role": "system", "content": f'Error: Please try again, details: {str(e)}'}
#             # assistant_message=f"System: Error: Please try again, details: {str(e)}"
#             st.session_state.chat_hist.append(assistant_message)
#             # return convo
#             return {
#                 "messages": st.session_state.chat_hist
#             }

#     elif "Query intent" in result:
        
#         try:
#             print("Kickoff Flow command triggered")
#             # api_results = api_results[3:]
#             try:
#                 result = kickoff(st.session_state.chat_hist)
#                 print(f'App:"{result}')
#             except Exception as e:
#                 print("ERROR while executing Kickoff !")



#             print("Score checks:",checks," and flag raised:", flag)

            
#             try:
#                 assistant_message = {"role": "system", "content": result}
#                 st.session_state.chat_hist.append(assistant_message)

#                 # Return the serialized response
#                 return {
#                     "messages": st.session_state.chat_hist
#                 }
                
#             except:
#                 assistant_message = {"role": "system", "content": f"Error processing output: Detail: {result}"}
#                 st.session_state.chat_hist.append(assistant_message)

#                 # Return the serialized response
#                 return {
#                     "messages": st.session_state.chat_hist
#                 }


#         # except HTTPException as e:
#         except Exception as e:
#             print(f"Error in API call: {e}")
#             assistant_message = {"role": "system", "content": f'Error: Please try again, details: {str(e)}'}
#             st.session_state.chat_hist.append(assistant_message)
#             # return convo
#             return {
#                 "messages": st.session_state.chat_hist
#             }

#     # return(f'AI response to question: {ques}')


st.title('StockSphere AI')
# st.write(st.session_state.chat_hist)
#### render chat history
# if not st.session_state.chat_init:
for resp in st.session_state.chat_hist[:-1]:
    role='ai' if resp['role']=='system' else 'user'
    role_bot=st.chat_message(role)
    role_bot.write(resp['content'])


#### current turn
user_input=st.chat_input("ask something...")
if user_input:
    # if st.session_state.chat_init:
    user=st.chat_message("user")
    user.write(user_input)
    st.session_state.chat_hist.append({"content":user_input,"role":"user"})
    # user_input=None

    # st.write(st.session_state.chat_hist)
    with st.spinner('generating response'):
        ai_resp_ls=run_stocksphere({"messages": st.session_state.chat_hist})
    # if st.session_state.chat_init:
        # user=st.chat_message("user")
        # user.write(user_input)
        ai_resp=ai_resp_ls['messages'][-1]['content']
        aibot=st.chat_message("ai")
    aibot.write(ai_resp)


    # aibot.write(ai_resp)
    # ai_resp_json={'content':ai_resp,'role':'ai'}
    st.session_state.chat_hist.append({"content":ai_resp,"role":"system"})


