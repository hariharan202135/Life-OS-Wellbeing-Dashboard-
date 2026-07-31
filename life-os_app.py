import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from google import genai
import urllib.parse

load_dotenv()
api_key=os.getenv("GEMINI_API_KEY")
if not api_key:
   st.error("Api key not found")
   st.stop()

client=genai.Client(api_key=api_key)

st.title("📱 Life-OS Wellbeing Dashboard")

st.write("Track your digital habits and receive AI-powered productivity coaching.")  

try:
    df = pd.read_csv("screentime.csv")

    st.subheader("📋 Screen Time Data")
    st.dataframe(df)

except FileNotFoundError:
    st.error("screentime.csv file not found.")
    
dates = sorted(df["Date"].unique())

with st.sidebar:
    st.header("Dashboard Controls")
    selected_date = st.selectbox(
    "Select a Date",
    dates
)
    daily_goal = st.slider(
    "Daily Screen Time Goal (minutes)",
    min_value=60,
    max_value=600,
    value=240,
    step=30
)
st.write("Selected Date:", selected_date)
st.write("Daily Goal:", daily_goal, "minutes")

today_data = df[df["Date"] == selected_date]
total_minutes = today_data["Minutes_Used"].sum()
most_used_app = today_data.loc[
    today_data["Minutes_Used"].idxmax(),
    "App_Name"
]
difference = total_minutes - daily_goal

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "Today's Screen Time",
        f"{total_minutes} min"
    )
with col2:
    st.metric(
        "Most Used App",
        most_used_app
    )
with col3:
    st.metric(
        "Goal Difference",
        f"{difference} min",
        delta=difference,
        delta_color="inverse"
    )

daily_usage = df.groupby("Date")["Minutes_Used"].sum()
st.subheader("📈 14-Day Screen Time Trend")
st.bar_chart(daily_usage)

category_summary = (
    today_data
    .groupby("Category")["Minutes_Used"]
    .sum()
)
summary_text = category_summary.to_string()
st.subheader("Today's Summary")

st.text(summary_text)
prompt = f"""
You are an expert AI Productivity Coach and an award-winning Hollywood Concept Artist.

Analyze the user's screen time data below.

Today's Screen Time Summary:
{summary_text}

Your task has TWO parts.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 1 — Productivity Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Give a detailed analysis with the following headings:

## 📊 Overall Score
Give a wellbeing score out of 100.

## 👍 Positive Habits
Mention productive activities.

## ⚠️ Areas of Concern
Explain unhealthy habits and why they are harmful.

## 🌿 Healthier Replacements
Suggest realistic offline activities such as:
- Walking
- Gym
- Reading books
- Cycling
- Meditation
- Playing outdoor games
- Learning a new skill
- Spending time with family
- Meal preparation

## 🎯 Tomorrow's Challenge
Give a small challenge the user can complete tomorrow.

## 💬 Motivation
End with one inspiring motivational quote.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 2 — Cinematic Avatar Prompt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Now create ONE extremely detailed image generation prompt.

The prompt should be suitable for a professional AI image generator.

The image should have:

• cinematic lighting
• ultra realistic
• highly detailed
• dramatic composition
• vibrant colors
• volumetric lighting
• depth of field
• masterpiece quality
• 8K
• digital art
• Unreal Engine quality
• sharp focus

If the screen time is GOOD:
Create an inspiring hero scene.

Examples:
- focused software engineer
- disciplined student
- productive programmer
- healthy lifestyle
- modern workspace
- warm sunlight
- books
- laptop
- plants
- coffee
- confidence
- success

If the screen time is BAD:
Create a symbolic scene.

Examples:
- lonely person surrounded by floating social media icons
- exhausted programmer
- zombie staring at a glowing smartphone
- dark room
- blue phone light
- messy desk
- junk food
- late night
- tired eyes
- dramatic shadows

The image should NOT contain:
- text
- logos
- watermarks
- UI elements
- low quality
- blurry objects

Return ONLY this format exactly:

Image Prompt:
<single detailed image prompt>

Do not write anything after Image Prompt.
"""

st.subheader("🤖 AI Wellbeing Coach")

if st.button("🧠 Analyze My Day"):

    with st.spinner("Analyzing your screen time..."):

        # Send prompt to Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # Store Gemini response
        ai_response = response.text

        # Separate analysis and image prompt
        if "Image Prompt:" in ai_response:
            analysis = ai_response.split("Image Prompt:")[0].strip()
            image_prompt = ai_response.split("Image Prompt:")[-1].strip()
        else:
            analysis = ai_response
            image_prompt = ""

        # Show screen time status
        if total_minutes > daily_goal:
            st.warning("⚠️ You exceeded your daily screen time goal.")
        else:
            st.info("✅ Great job! You stayed within your daily goal.")

        # Show Gemini analysis
        st.markdown(analysis)

        # Generate and display avatar
        if image_prompt:

            # Enhance the prompt for better image quality
            image_prompt += (
                ", cinematic lighting, ultra realistic, masterpiece, "
                "8K, highly detailed, Unreal Engine 5, "
                "volumetric lighting, depth of field, dramatic composition, "
                "vibrant colors, sharp focus, award-winning digital art"
            )

            # Encode prompt for URL
            encoded_prompt = urllib.parse.quote(image_prompt)

            # Pollinations AI image URL
            image_url = (
                f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            )

            st.markdown("---")
            st.subheader("🖼️ Your AI Lifestyle Avatar")

            st.image(
                image_url,
                caption="Generated from your digital wellbeing habits",
                use_container_width=True
            )

            # Show image prompt (optional)
            with st.expander("🎨 View Image Prompt"):
                st.code(image_prompt)

        else:
            st.error("❌ Gemini did not return an image prompt.")