import streamlit as st
import openai
import razorpay
from datetime import datetime, timedelta

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Fari - AI Assistant", layout="centered")
st.title("🤖 Fari - Your AI Assistant")

# Store API keys securely using Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
RAZORPAY_KEY_ID = st.secrets["RAZORPAY_KEY_ID"]
RAZORPAY_KEY_SECRET = st.secrets["RAZORPAY_KEY_SECRET"]

# -------------------- PAYMENT --------------------
# Create Razorpay client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Session state to manage access
if "paid" not in st.session_state:
    st.session_state.paid = False

# -------------------- PAYMENT OPTIONS --------------------
st.subheader("💳 Unlock Access")
option = st.radio("Choose a plan:", ("One-time Access - ₹10", "Monthly Access - ₹99"))

if st.button("Pay Now"):
    amount = 1000 if option == "One-time Access - ₹10" else 9900
    payment = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    st.session_state.order_id = payment['id']
    st.success("Order Created. Please pay via Razorpay checkout link.")
    checkout_url = f"https://api.razorpay.com/v1/checkout/embedded?order_id={payment['id']}"
    st.markdown(f"[👉 Click here to Pay]({checkout_url})")
    st.info("After payment, refresh this page and click 'Verify Payment'")

if st.button("Verify Payment"):
    try:
        order = client.order.fetch(st.session_state.order_id)
        payments = client.order.payments(order['id'])
        if payments['count'] > 0 and payments['items'][0]['status'] == 'captured':
            st.session_state.paid = True
            st.success("✅ Payment Verified. You can now chat with Fari!")
        else:
            st.error("❌ Payment not completed. Please try again.")
    except Exception as e:
        st.error(f"Error verifying payment: {e}")

# -------------------- CHATBOT --------------------
if st.session_state.paid:
    user_input = st.text_input("You:")
    if user_input:
        with st.spinner("Thinking..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_input}]
                )
                reply = response.choices[0].message.content
                st.text_area("Fari:", value=reply, height=200)
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.warning("🔒 Please complete payment to use the chatbot.")
