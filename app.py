import streamlit as st
import pandas as pd
import plotly.express as px
#1. Dashboard Layout Settings
st.set_page_config(page_title="Customer Churn Dashboard", layout="wide")

#2. Data Loading 
@st.cache_data
def load_data():
    data = pd.read_excel("European Bank.xlsx")
    return data
data = load_data()
#3. Sidebar Navigation Menu
st.sidebar.title("Customer Engagement & Product Utilization Analytics for Retention Strategy")
selection = st.sidebar.radio("Go to:", ["Dashboard Overview", "Task: Engagement Classification", "Task: Product Utilization Analysis", "Task: Financial Commitment vs Engagement Analysis", "Task: Retention Strength Assessment" ])
#4. Main Content Area
if selection == "Dashboard Overview":
    st.title("Customers Retention Analysis Dashboard")
    st.write("This dashboard provides insights into a multi-phase analysis of customer churn, engagement, and product utilization to help inform retention strategies.")
    st.metric(label="Total Customers", value=len(data))
    st.dataframe(data.head())
#Task 1: Engagement Classification    
elif selection == "Task: Engagement Classification":
    st.header("Customer Engagement Classification")
    st.write("This section classifies the customers into four engagement categories based on their activity levels and product consumption.")

    #1. The logic for classifying customers into engagement categories
    data['EngagementProfile'] = 'Unclassified' #Placeholder for engagement profile
    data.loc[(data['IsActiveMember'] == 1) & (data['NumOfProducts'] >= 2) & (data['HasCrCard'] == 1) & (data['CreditScore'] >= 500), 'EngagementProfile'] = 'Active engaged customers'
    data.loc[(data['IsActiveMember'] == 0) & (data['NumOfProducts'] == 1) & (data['HasCrCard'] == 0) & (data['CreditScore'] < 500), 'EngagementProfile'] = 'Inactive Disengaged Customers'
    data.loc[(data['IsActiveMember'] == 1) & (data['NumOfProducts'] == 2) & (data['HasCrCard'] == 1) & (data['CreditScore'] >= 500), 'EngagementProfile'] = 'Active but low-product customers'
    data.loc[(data['IsActiveMember'] == 0) & (data['Balance'] > 100000), 'EngagementProfile'] = 'Inactive high-balance customers'

    #2. Segmenting customers into engagement profiles and calculating the count for each profile
    st.subheader("Inspecting Customer Engagement Profiles")
    st.write("Select an engagement profile to view the count of customers:")

    #Dropdown menu for selecting engagement profile
    target_profile = st.selectbox("Select Engagement Profile", options=data['EngagementProfile'].unique())

    #Filtering data based on selected engagement profile and displaying count
    filtered_data = data[data['EngagementProfile'] == target_profile].head(5)

    if not filtered_data.empty:
        st.success(f"Displaying data for: {target_profile}")
        st.table(filtered_data[['CustomerId', 'Surname', 'Geography', 'CreditScore', 'Balance', 'NumOfProducts', 'IsActiveMember', 'Gender']])
    else:
        st.warning(f"No customers found for the selected engagement profile: {target_profile}")

    #3. Displaying the count of customers in each engagement profile
    fig = px.bar(data['EngagementProfile'].value_counts(), x='count', title='Count of Customers in Each Engagement Profile')
    st.plotly_chart(fig, use_container_width=True)

#Task 2: Product Utilization Analysis
elif selection == "Task: Product Utilization Analysis":
    st.header("Product Utilization & Retention Depth Analysis")
    st.write("This section identifies the 'Sweet Spot' of product utilization and correlates with customer churn.")

    #1. Grouping customers based on the number of products they use and calculating churn rates for each group
    product_utilization = data.groupby('NumOfProducts')['Exited'].mean().reset_index()
    product_utilization['Churn Rate (%)'] = product_utilization['Exited'] * 100

    #2. Key insights regarding the 'Sweet Spot' of product utilization and its correlation with churn
    col1, col2 = st.columns(2)

    #Finding the lowest churn rate and corresponding number of products
    sweet_spot = product_utilization.loc[product_utilization['Churn Rate (%)'].idxmin(), 'NumOfProducts']
    min_churn_rate = product_utilization['Churn Rate (%)'].min()

    col1.metric(label="Optimal Number of Product Utilization", value=f"{(sweet_spot)} Products")
    col2.metric(label="Minimum Churn Rate", value=f"{(min_churn_rate):.2f}%")

    #3. Visualizing the relationship between product utilization and churn rates
    fig = px.bar(product_utilization, x='NumOfProducts', y='Churn Rate (%)', text='Churn Rate (%)', title='Churn Rate by Number of Products Utilized', labels={'NumOfProducts': 'Number of Products Utilized', 'Churn Rate (%)': 'Churn Rate (%)'}, color ='Churn Rate (%)', color_continuous_scale='RdYlGn_r')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    #4. Providing actionable recommendations for optimizing product offerings based on the analysis
    st.info(f"""Actionable Recommendations: Customers with {int(sweet_spot)} products have the lowest churn rate, and hence the most stable segment. A sudden hike in churn for customers with 3 or 4 products indicates 'Product Overload' or 'Product Overlap' or 'Product Underutilization', where the products no longer meet their core financial needs. Focus on promoting additional products to customers with fewer products to move them towards the 'Sweet Spot' and reduce churn.""")

#Task 3: Financial Commitment vs Engagement Analysis
elif selection == "Task: Financial Commitment vs Engagement Analysis":
    st.header("Economic Positioning: Financial Commitment vs Engagement Analysis")
    st.write("This section identifies 'Flight Risk' customers: those with high salaries but low engagement levels")
             
    #1. Define the Mismatch Logic to identify 'Flight Risk' customers based on high salaries but low engagement levels
    #People in the 'Inactive high-balance customers' profile are considered 'Flight Risk' customers due to their high financial commitment (high balance) but low engagement (inactive status).
    #Look for the top 25% of salary but bottom 25% of balance to identify 'Flight Risk' customers
    salary_threshold = data['EstimatedSalary'].quantile(0.75)
    balance_threshold = data['Balance'].quantile(0.25)

    data['FinancialEngagementProfile'] = 'Aligned'
    data.loc[(data['EstimatedSalary'] >= salary_threshold) & (data['Balance'] <= balance_threshold), 'FinancialEngagementProfile'] = 'Mismatched (High Salary, Low Engagement)'

    #2. Statistics on the number of 'Flight Risk' customers and their characteristics
    mismatch_count = len(data[data['FinancialEngagementProfile'] == 'Mismatched (High Salary, Low Engagement)'])
    mismatch_churn_rate = data[data['FinancialEngagementProfile'] == 'Mismatched (High Salary, Low Engagement)']['Exited'].mean() * 100

    col1, col2 = st.columns(2)
    col1.metric(label="Number of Mismatched Customers", value=mismatch_count)
    col2.metric(label="Churn Rate of Mismatched Customers", value=f"{mismatch_churn_rate:.1f}%")

    #3. Visualizations comparing the financial commitment and engagement levels of 'Flight Risk' customers against other segments
    st.subheader("Visualizing the Mismatch Zone")
    fig = px.scatter(data, x='EstimatedSalary', y='Balance', color='FinancialEngagementProfile', title="Economic Positioning: Salary vs. Balance", color_discrete_map={'Aligned': 'green', 'Mismatched (High Salary, Low Engagement)': 'red'}, opacity=0.5)

    # Adding lines to indicate the thresholds for salary and balance (the 'Mismatch Zone'/'Danger Zone')
    st.plotly_chart(fig, use_container_width=True)

    #4. Actionable insights for targeting 'Flight Risk' customers with tailored retention strategies
    st.warning(f"""Actionable Insights: There are {mismatch_count} customers who earn over {salary_threshold:.0f} but keep less than {balance_threshold:.0f} in their accounts. This shows that the bank is facing a potential mismatch between financial commitment and engagement levels. Customers in the 'Mismatched (High Salary, Low Engagement)' segment are at a higher risk of churn due to their high financial commitment but low engagement. Tailored retention strategies such as personalized offers, targeted communication, and proactive customer service can help re-engage these customers and reduce churn.""") 

#Task 4: Retention Strength Assessment
elif selection == "Task: Retention Strength Assessment":
    st.header("Comprehensive Retention Strength Score: Engagement Profiles & Churn Rates")
    st.write("This section assesses the overall retention strength of the customer base by analyzing the distribution of engagement profiles and their corresponding churn rates. The model calculates the 'Loyality Strength Score' (0-3) for each engagement profile, which combines the proportion of customers in each profile with their respective churn rates to provide a holistic view of retention strength.")
    
    #1. The scoring model for calculating the 'Loyality Strength Score' for each engagement profile based on the distribution of customers and their churn rates
    # Start with 0 points for each profile
    data['RetentionStrengthScore'] = 0
    
    #Point 1: Engagement Profile Distribution [Is an Active Engaged Customer?]
    data.loc[data['IsActiveMember'] == 1, 'RetentionStrengthScore'] += 1

    #Point 2: Product Utilization [Has exactly 2 products?]
    data.loc[data['NumOfProducts'] == 2, 'RetentionStrengthScore'] += 1

    #Point 3: Financial Alignment [Not a Mismatched customer?]
    salary_q3 = data['EstimatedSalary'].quantile(0.75)
    balance_q1 = data['Balance'].quantile(0.25)
    mismatch_condition = (data['EstimatedSalary'] >= salary_q3) & (data['Balance'] <= balance_q1)
    data.loc[~mismatch_condition, 'RetentionStrengthScore'] += 1

    #2. Categorizing the retention strength into 'Low', 'Medium', and 'High' based on the calculated scores
    score_map = {0: 'Fragile Retention', 1: 'Low Stability Retention', 2: 'Stable Retention', 3: 'Sticky Retention (High Loyalty)'}
    data['RetentionStrengthLevel'] = data['RetentionStrengthScore'].map(score_map)

    loyality_counts = data['RetentionStrengthLevel'].value_counts().reset_index()
    loyality_counts.columns = ['RetentionStrengthLevel', 'Count']

    #Sort the levels in the order of Fragile, Low Stability, Stable, Sticky
    level_order = ['Sticky Retention (High Loyalty)', 'Stable Retention', 'Low Stability Retention', 'Fragile Retention']
    loyality_counts['RetentionStrengthLevel'] = pd.Categorical(loyality_counts['RetentionStrengthLevel'], categories=level_order, ordered=True)
    loyality_counts = loyality_counts.sort_values('RetentionStrengthLevel')

    #3. Visualizations showing the distribution of retention strength levels across the customer base and their corresponding churn rates: Loyality Strength Score vs Churn Rate
    fig = px.funnel(loyality_counts, x = 'Count', y = 'RetentionStrengthLevel', title='Customer Retention Funnel: Retention Strength Levels', color_discrete_sequence= px.colors.sequential.Greens_r)
    st.plotly_chart(fig, use_container_width=True)

    #4. Actionable recommendations for strengthening retention strategies based on the assessment results
    st.success(f"""Recommendations: The analysis reveals that only **{len(data[data['RetentionStrengthScore'] == 3])}** customers hit all three loyality markers. The 'Sticky Retention (High Loyalty)' segment represents customers with the strongest retention strength, while the 'Fragile Retention' segment represents those with the weakest retention strength. Focus on strategies to move customers from 'Fragile Retention' to 'Stable Retention' and ultimately to 'Sticky Retention' by enhancing engagement, optimizing product offerings, and ensuring financial alignment. Tailored interventions for each retention strength level can help improve overall customer loyalty and reduce churn.""")
    
    #5. Final summary of all tasks and their implications for the bank's retention strategy
    st.info(f"""Summary: This comprehensive analysis of customer engagement, product utilization, financial commitment, and retention strength provides valuable insights for the bank's retention strategy. By understanding the distribution of engagement profiles, identifying the 'Sweet Spot' of product utilization, assessing financial alignment, and categorizing retention strength, the bank can implement targeted strategies to enhance customer loyalty and reduce churn. Focusing on high-risk segments such as 'Mismatched (High Salary, Low Engagement)' customers and those in the 'Fragile Retention' category will be crucial for improving overall retention rates and fostering long-term customer relationships.""")

    #6. Export for the final dataset with the calculated retention strength scores and levels for further analysis or reporting
    st.subheader("Export Processed Data")
    st.write("You can download the processed dataset with the calculated retention strength scores and levels for further analysis or reporting.")
    st.download_button("Download Processed Data", data.to_csv(index=False), file_name="processed_customer_data.csv", mime="text/csv")

# End of the Streamlit app code
# This code creates a comprehensive customer churn dashboard with multiple tasks analyzing engagement, product utilization, financial commitment, and retention strength. Each task provides insights and actionable recommendations to inform the bank's retention strategy. The final section allows users to export the processed dataset for further analysis.
    