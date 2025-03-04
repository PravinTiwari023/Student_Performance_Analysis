import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# Page configuration
st.set_page_config(page_title="Student Performance Dashboard", layout="wide")

# Load data functions
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('StudentData.xlsx', sheet_name='Student information')
        return df
    except Exception as e:
        st.error(f"Error loading student info data: {e}")
        return None

@st.cache_data
def load_test_data(sheet_name):
    try:
        test_df = pd.read_excel('StudentData.xlsx', sheet_name=sheet_name)
        return test_df
    except Exception as e:
        st.error(f"Error loading {sheet_name} data: {e}")
        return None

# Main application
def main():
    st.title("🎓 Student Performance Dashboard")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Define test maximum scores
    test_max_scores = {
        "Test 1": 20,
        "Surprise Test": 20,
        "Test 2": 20,
        "Unit Test": 50
    }
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a View", [
        "Overview", 
        "Student Details", 
        "Performance Analysis", 
        "Contact Information"
    ])
    
    # Overview Page
    if page == "Overview":
        st.header("Student Performance Overview")
        
        # Total number of students
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Students", len(df))
        
        # Load all test data for overview
        test1_df = load_test_data("Test 1")
        surprise_df = load_test_data("Surprise Test")
        test2_df = load_test_data("Test 2")
        unit_df = load_test_data("Unit Test")
        
        if all([test1_df is not None, surprise_df is not None, test2_df is not None, unit_df is not None]):
            # Calculate class averages as percentages
            subject_cols = ["English Score", "Maths Score", "Science Score", "SST Score", "Hindi", "Marathi"]
            
            with col2:
                # Display test score information
                st.info("📊 Test 1, Test 2, Surprise Test: Maximum score of 20 points\n\nUnit Test: Maximum score of 50 points")
            
            # Performance metrics
            st.subheader("Class Performance Metrics")
            
            # Calculate overall averages as percentages
            test1_pct = (test1_df[subject_cols].mean().mean() / test_max_scores["Test 1"]) * 100
            surprise_pct = (surprise_df[subject_cols].mean().mean() / test_max_scores["Surprise Test"]) * 100
            test2_pct = (test2_df[subject_cols].mean().mean() / test_max_scores["Test 2"]) * 100
            unit_pct = (unit_df[subject_cols].mean().mean() / test_max_scores["Unit Test"]) * 100
            
            # Display metrics
            metric_cols = st.columns(4)
            with metric_cols[0]:
                st.metric("Test 1 Performance", f"{test1_pct:.1f}%", 
                          delta=f"{test1_df[subject_cols].mean().mean():.1f}/20")
            with metric_cols[1]:
                st.metric("Surprise Test Performance", f"{surprise_pct:.1f}%", 
                          delta=f"{surprise_df[subject_cols].mean().mean():.1f}/20")
            with metric_cols[2]:
                st.metric("Test 2 Performance", f"{test2_pct:.1f}%", 
                          delta=f"{test2_df[subject_cols].mean().mean():.1f}/20")
            with metric_cols[3]:
                st.metric("Unit Test Performance", f"{unit_pct:.1f}%", 
                          delta=f"{unit_df[subject_cols].mean().mean():.1f}/50")
            
            # Performance trend chart
            st.subheader("Performance Trends")
            
            # Create normalized scores for comparison
            test_names = ['Test 1', 'Surprise Test', 'Test 2', 'Unit Test']
            test_avgs_pct = [test1_pct, surprise_pct, test2_pct, unit_pct]
            
            fig = px.line(
                x=test_names, 
                y=test_avgs_pct,
                markers=True,
                labels={"x": "Test", "y": "Average Score (%)"},
                title="Class Average Performance Across Tests (Percentage)"
            )
            fig.update_layout(
                xaxis=dict(tickmode='linear'),
                yaxis=dict(range=[0, 100]),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Subject performance comparison
            st.subheader("Subject Performance Comparison")
            
            # Calculate subject averages across tests (as percentages)
            subject_data = []
            
            for subject in subject_cols:
                subject_data.append({
                    "Subject": subject,
                    "Test 1": (test1_df[subject].mean() / test_max_scores["Test 1"]) * 100,
                    "Surprise Test": (surprise_df[subject].mean() / test_max_scores["Surprise Test"]) * 100,
                    "Test 2": (test2_df[subject].mean() / test_max_scores["Test 2"]) * 100,
                    "Unit Test": (unit_df[subject].mean() / test_max_scores["Unit Test"]) * 100
                })
            
            subject_df = pd.DataFrame(subject_data)
            
            # Create a heatmap for subject performance
            fig = px.imshow(
                subject_df[["Test 1", "Surprise Test", "Test 2", "Unit Test"]].values,
                x=test_names,
                y=subject_df["Subject"],
                color_continuous_scale="RdYlGn",
                labels=dict(x="Test", y="Subject", color="Score (%)"),
                text_auto='.1f',
                aspect="auto"
            )
            fig.update_layout(title="Subject Performance Heatmap (%)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Top performers across all tests
            st.subheader("Top Performers Overall")
            
            # Merge all test data with student info
            student_info = df[['Student ID', 'Name']]
            
            # Calculate overall student performance
            test1_with_names = pd.merge(test1_df, student_info, on='Student ID')
            surprise_with_names = pd.merge(surprise_df, student_info, on='Student ID')
            test2_with_names = pd.merge(test2_df, student_info, on='Student ID')
            unit_with_names = pd.merge(unit_df, student_info, on='Student ID')
            
            # Calculate normalized scores (as percentage of max possible)
            test1_with_names['Normalized Score'] = (test1_with_names[subject_cols].sum(axis=1) / (len(subject_cols) * test_max_scores["Test 1"])) * 100
            surprise_with_names['Normalized Score'] = (surprise_with_names[subject_cols].sum(axis=1) / (len(subject_cols) * test_max_scores["Surprise Test"])) * 100
            test2_with_names['Normalized Score'] = (test2_with_names[subject_cols].sum(axis=1) / (len(subject_cols) * test_max_scores["Test 2"])) * 100
            unit_with_names['Normalized Score'] = (unit_with_names[subject_cols].sum(axis=1) / (len(subject_cols) * test_max_scores["Unit Test"])) * 100
            
            # Get top 5 students from each test
            top_test1 = test1_with_names[['Student ID', 'Name', 'Normalized Score']].rename(columns={'Normalized Score': 'Test 1 Score (%)'}).sort_values('Test 1 Score (%)', ascending=False).head(5)
            top_surprise = surprise_with_names[['Student ID', 'Name', 'Normalized Score']].rename(columns={'Normalized Score': 'Surprise Test Score (%)'}).sort_values('Surprise Test Score (%)', ascending=False).head(5)
            top_test2 = test2_with_names[['Student ID', 'Name', 'Normalized Score']].rename(columns={'Normalized Score': 'Test 2 Score (%)'}).sort_values('Test 2 Score (%)', ascending=False).head(5)
            top_unit = unit_with_names[['Student ID', 'Name', 'Normalized Score']].rename(columns={'Normalized Score': 'Unit Test Score (%)'}).sort_values('Unit Test Score (%)', ascending=False).head(5)
            
            # Display top performers in columns
            top_cols = st.columns(4)
            with top_cols[0]:
                st.write("**Test 1 Top Performers**")
                st.dataframe(top_test1[['Name', 'Test 1 Score (%)']], hide_index=True)
            with top_cols[1]:
                st.write("**Surprise Test Top Performers**")
                st.dataframe(top_surprise[['Name', 'Surprise Test Score (%)']], hide_index=True)
            with top_cols[2]:
                st.write("**Test 2 Top Performers**")
                st.dataframe(top_test2[['Name', 'Test 2 Score (%)']], hide_index=True)
            with top_cols[3]:
                st.write("**Unit Test Top Performers**")
                st.dataframe(top_unit[['Name', 'Unit Test Score (%)']], hide_index=True)
        
        else:
            st.error("Could not load all test data. Please check the Excel file.")
            
        # Basic statistics column
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Students by first letter of name
            name_distribution = df['Name'].str[0].value_counts()
            fig = px.pie(
                names=name_distribution.index, 
                values=name_distribution.values, 
                title="Students by Name Initial"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Phone number distribution
            phone_prefix = df['Phone Number'].astype(str).str[:3].value_counts()
            fig = px.bar(
                x=phone_prefix.index, 
                y=phone_prefix.values, 
                title="Phone Number Prefixes"
            )
            st.plotly_chart(fig, use_container_width=True)
        with col3:
            # Parent contact distribution
            parent_phone_prefix = df['Parent Phone Number'].astype(str).str[:3].value_counts()
            fig = px.bar(
                x=parent_phone_prefix.index, 
                y=parent_phone_prefix.values, 
                title="Parent Phone Number Prefixes"
            )
            st.plotly_chart(fig, use_container_width=True)
    # Student Details Page
    elif page == "Student Details":
        st.header("Student Details")
        
        # Search and filter students
        search_term = st.text_input("Search Students by Name or ID")
        
        if search_term:
            filtered_df = df[
                df['Name'].str.contains(search_term, case=False) | 
                df['Student ID'].astype(str).str.contains(search_term)
            ]
        else:
            filtered_df = df
            
        # Display students in a table
        st.dataframe(filtered_df, use_container_width=True)
        
        # Select a student for detailed view
        selected_student = st.selectbox("Select a Student for Detailed View", filtered_df['Name'])
        
        if selected_student:
            student_details = filtered_df[filtered_df['Name'] == selected_student].iloc[0]
            
            # Display student details in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Student ID:** {student_details['Student ID']}")
                st.write(f"**Name:** {student_details['Name']}")
                st.write(f"**Email:** {student_details['Email']}")
            
            with col2:
                st.write(f"**Phone Number:** {student_details['Phone Number']}")
                st.write(f"**Parent Phone Number:** {student_details['Parent Phone Number']}")
    # Performance Analysis Page
    elif page == "Performance Analysis":
        st.header("Performance Analysis")
        
        # Add tabs for different test types
        test_tab = st.tabs(["Test 1", "Surprise Test", "Test 2", "Unit Test", "Overall Performance"])
        # Test 1 Tab
        with test_tab[0]:
            test1_df = load_test_data("Test 1")
            if test1_df is not None:
                st.subheader("Test 1 Results (Maximum Score: 20)")
                        
                # Summary statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_english = test1_df["English Score"].mean()
                    avg_maths = test1_df["Maths Score"].mean()
                    st.metric("Avg. English Score", f"{avg_english:.1f}/20", delta=f"{(avg_english/20)*100:.1f}%")
                    st.metric("Avg. Maths Score", f"{avg_maths:.1f}/20", delta=f"{(avg_maths/20)*100:.1f}%")
                
                with col2:
                    avg_science = test1_df["Science Score"].mean()
                    avg_sst = test1_df["SST Score"].mean()
                    st.metric("Avg. Science Score", f"{avg_science:.1f}/20", delta=f"{(avg_science/20)*100:.1f}%")
                    st.metric("Avg. SST Score", f"{avg_sst:.1f}/20", delta=f"{(avg_sst/20)*100:.1f}%")
                
                with col3:
                    avg_hindi = test1_df["Hindi"].mean()
                    avg_marathi = test1_df["Marathi"].mean()
                    st.metric("Avg. Hindi Score", f"{avg_hindi:.1f}/20", delta=f"{(avg_hindi/20)*100:.1f}%")
                    st.metric("Avg. Marathi Score", f"{avg_marathi:.1f}/20", delta=f"{(avg_marathi/20)*100:.1f}%")
                
                # Subject-wise performance chart
                st.subheader("Subject-wise Performance")
                subject_cols = ["English Score", "Maths Score", "Science Score", "SST Score", "Hindi", "Marathi"]
                subject_avgs = [test1_df[col].mean() for col in subject_cols]
                subject_pcts = [(avg / 20) * 100 for avg in subject_avgs]
                
                # Create a more informative bar chart with percentages
                fig = px.bar(
                    x=subject_cols,
                    y=subject_avgs,
                    labels={"x": "Subject", "y": "Average Score"},
                    title="Average Scores by Subject (out of 20)",
                    text=[f"{avg:.1f} ({pct:.1f}%)" for avg, pct in zip(subject_avgs, subject_pcts)]
                )
                fig.update_layout(
                    yaxis=dict(range=[0, 20]),
                    uniformtext_minsize=8,
                    uniformtext_mode='hide'
                )
                st.plotly_chart(fig, use_container_width=True)
        # Surprise Test Tab
        with test_tab[1]:
            surprise_df = load_test_data("Surprise Test")
            if surprise_df is not None:
                st.subheader("Surprise Test Results (Maximum Score: 20)")
                
                # Summary statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_english = surprise_df["English Score"].mean()
                    avg_maths = surprise_df["Maths Score"].mean()
                    st.metric("Avg. English Score", f"{avg_english:.1f}/20", delta=f"{(avg_english/20)*100:.1f}%")
                    st.metric("Avg. Maths Score", f"{avg_maths:.1f}/20", delta=f"{(avg_maths/20)*100:.1f}%")
                
                with col2:
                    avg_science = surprise_df["Science Score"].mean()
                    avg_sst = surprise_df["SST Score"].mean()
                    st.metric("Avg. Science Score", f"{avg_science:.1f}/20", delta=f"{(avg_science/20)*100:.1f}%")
                    st.metric("Avg. SST Score", f"{avg_sst:.1f}/20", delta=f"{(avg_sst/20)*100:.1f}%")
                
                with col3:
                    avg_hindi = surprise_df["Hindi"].mean()
                    avg_marathi = surprise_df["Marathi"].mean()
                    st.metric("Avg. Hindi Score", f"{avg_hindi:.1f}/20", delta=f"{(avg_hindi/20)*100:.1f}%")
                    st.metric("Avg. Marathi Score", f"{avg_marathi:.1f}/20", delta=f"{(avg_marathi/20)*100:.1f}%")
                        
                    # Subject-wise performance chart
                    st.subheader("Subject-wise Performance")
                    subject_cols = ["English Score", "Maths Score", "Science Score", "SST Score", "Hindi", "Marathi"]
                    subject_avgs = [surprise_df[col].mean() for col in subject_cols]
                    subject_pcts = [(avg / 20) * 100 for avg in subject_avgs]
                    
                    # Create a more informative bar chart with percentages
                    fig = px.bar(
                        x=subject_cols,
                        y=subject_avgs,
                        labels={"x": "Subject", "y": "Average Score"},
                        title="Average Scores by Subject (out of 20)",
                        text=[f"{avg:.1f} ({pct:.1f}%)" for avg, pct in zip(subject_avgs, subject_pcts)]
                    )
                    fig.update_layout(
                        yaxis=dict(range=[0, 20]),
                        uniformtext_minsize=8,
                        uniformtext_mode='hide'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        # Test 2 Tab
                with test_tab[2]:
                    test2_df = load_test_data("Test 2")
                    if test2_df is not None:
                        st.subheader("Test 2 Results (Maximum Score: 20)")
                        
                        # Summary statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            avg_english = test2_df["English Score"].mean()
                            avg_maths = test2_df["Maths Score"].mean()
                            st.metric("Avg. English Score", f"{avg_english:.1f}/20", delta=f"{(avg_english/20)*100:.1f}%")
                            st.metric("Avg. Maths Score", f"{avg_maths:.1f}/20", delta=f"{(avg_maths/20)*100:.1f}%")
                        
                        with col2:
                            avg_science = test2_df["Science Score"].mean()
                            avg_sst = test2_df["SST Score"].mean()
                            st.metric("Avg. Science Score", f"{avg_science:.1f}/20", delta=f"{(avg_science/20)*100:.1f}%")
                            st.metric("Avg. SST Score", f"{avg_sst:.1f}/20", delta=f"{(avg_sst/20)*100:.1f}%")
                        
                        with col3:
                            avg_hindi = test2_df["Hindi"].mean()
                            avg_marathi = test2_df["Marathi"].mean()
                            st.metric("Avg. Hindi Score", f"{avg_hindi:.1f}/20", delta=f"{(avg_hindi/20)*100:.1f}%")
                            st.metric("Avg. Marathi Score", f"{avg_marathi:.1f}/20", delta=f"{(avg_marathi/20)*100:.1f}%")
                        
                        # Subject-wise performance chart
                        st.subheader("Subject-wise Performance")
                        subject_cols = ["English Score", "Maths Score", "Science Score", "SST Score", "Hindi", "Marathi"]
                        subject_avgs = [test2_df[col].mean() for col in subject_cols]
                        subject_pcts = [(avg / 20) * 100 for avg in subject_avgs]
                        
                        # Create a more informative bar chart with percentages
                        fig = px.bar(
                            x=subject_cols,
                            y=subject_avgs,
                            labels={"x": "Subject", "y": "Average Score"},
                            title="Average Scores by Subject (out of 20)",
                            text=[f"{avg:.1f} ({pct:.1f}%)" for avg, pct in zip(subject_avgs, subject_pcts)]
                        )
                        fig.update_layout(
                            yaxis=dict(range=[0, 20]),
                            uniformtext_minsize=8,
                            uniformtext_mode='hide'
                        )
                        st.plotly_chart(fig, use_container_width=True)
        # Unit Test Tab
        with test_tab[3]:
                    unit_df = load_test_data("Unit Test")
                    if unit_df is not None:
                        st.subheader("Unit Test Results (Maximum Score: 50)")
                        
                        # Summary statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            avg_english = unit_df["English Score"].mean()
                            avg_maths = unit_df["Maths Score"].mean()
                            st.metric("Avg. English Score", f"{avg_english:.1f}/50", delta=f"{(avg_english/50)*100:.1f}%")
                            st.metric("Avg. Maths Score", f"{avg_maths:.1f}/50", delta=f"{(avg_maths/50)*100:.1f}%")
                        
                        with col2:
                            avg_science = unit_df["Science Score"].mean()
                            avg_sst = unit_df["SST Score"].mean()
                            st.metric("Avg. Science Score", f"{avg_science:.1f}/50", delta=f"{(avg_science/50)*100:.1f}%")
                            st.metric("Avg. SST Score", f"{avg_sst:.1f}/50", delta=f"{(avg_sst/50)*100:.1f}%")
                        
                        with col3:
                            avg_hindi = unit_df["Hindi"].mean()
                            avg_marathi = unit_df["Marathi"].mean()
                            st.metric("Avg. Hindi Score", f"{avg_hindi:.1f}/50", delta=f"{(avg_hindi/50)*100:.1f}%")
                            st.metric("Avg. Marathi Score", f"{avg_marathi:.1f}/50", delta=f"{(avg_marathi/50)*100:.1f}%")
                        
                        # Subject-wise performance chart
                        st.subheader("Subject-wise Performance")
                        subject_cols = ["English Score", "Maths Score", "Science Score", "SST Score", "Hindi", "Marathi"]
                        subject_avgs = [unit_df[col].mean() for col in subject_cols]
                        subject_pcts = [(avg / 50) * 100 for avg in subject_avgs]
                        
                        # Create a more informative bar chart with percentages
                        fig = px.bar(
                            x=subject_cols,
                            y=subject_avgs,
                            labels={"x": "Subject", "y": "Average Score"},
                            title="Average Scores by Subject (out of 50)",
                            text=[f"{avg:.1f} ({pct:.1f}%)" for avg, pct in zip(subject_avgs, subject_pcts)]
                        )
                        fig.update_layout(
                            yaxis=dict(range=[0, 50]),
                            uniformtext_minsize=8,
                            uniformtext_mode='hide'
                        )
                        st.plotly_chart(fig, use_container_width=True)
        # Overall Performance Tab
        with test_tab[4]:
                    st.subheader("Overall Academic Performance")
                    
                    # Load all test data
                    test1_df = load_test_data("Test 1")
                    surprise_df = load_test_data("Surprise Test")
                    test2_df = load_test_data("Test 2")
                    unit_df = load_test_data("Unit Test")
                    
                    if all([test1_df is not None, surprise_df is not None, test2_df is not None, unit_df is not None]):
                        # Define test maximum scores
                        test_max_scores = {
                            "Test 1": 20,
                            "Surprise Test": 20,
                            "Test 2": 20,
                            "Unit Test": 50
                        }
                        
                        # Display test score information
                        st.info("📊 Test 1, Test 2, Surprise Test: Maximum score of 20 points\n\nUnit Test: Maximum score of 50 points")
                        
                        # Merge with student info
                        student_info = df[['Student ID', 'Name']]
                        
                        # Calculate average scores for each test
                        subject_cols = ["English Score", "Maths Score", "Science Score", "SST Score", "Hindi", "Marathi"]
                        
                        # Calculate normalized scores (as percentage of max possible)
                        test1_avg_pct = (test1_df[subject_cols].mean(axis=1) / 20) * 100
                        surprise_avg_pct = (surprise_df[subject_cols].mean(axis=1) / 20) * 100
                        test2_avg_pct = (test2_df[subject_cols].mean(axis=1) / 20) * 100
                        unit_avg_pct = (unit_df[subject_cols].mean(axis=1) / 50) * 100
                        
                        # Define test names for charts
                        test_names = ['Test 1', 'Surprise Test', 'Test 2', 'Unit Test']
                        
                        # Calculate subject averages across tests (as percentages)
                        subject_data = []
                        
                        for subject in subject_cols:
                            subject_data.append({
                                "Subject": subject,
                                "Test 1": (test1_df[subject].mean() / test_max_scores["Test 1"]) * 100,
                                "Surprise Test": (surprise_df[subject].mean() / test_max_scores["Surprise Test"]) * 100,
                                "Test 2": (test2_df[subject].mean() / test_max_scores["Test 2"]) * 100,
                                "Unit Test": (unit_df[subject].mean() / test_max_scores["Unit Test"]) * 100
                            })
                        
                        subject_df = pd.DataFrame(subject_data)
                        
                        # Create a radar chart for subject performance comparison
                        fig = go.Figure()
                        
                        for subject in subject_df["Subject"]:
                            subject_row = subject_df[subject_df["Subject"] == subject]
                            fig.add_trace(go.Scatterpolar(
                                r=subject_row.iloc[0, 1:].values,
                                theta=test_names,
                                fill='toself',
                                name=subject
                            ))
                        
                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 100]
                                )
                            ),
                            title="Subject Performance Across Tests (%)",
                            showlegend=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Grade distribution analysis
                        st.subheader("Grade Distribution Analysis")
                        
                        # Define grade ranges
                        def assign_grade(score):
                            if score >= 90:
                                return "A"
                            elif score >= 80:
                                return "B"
                            elif score >= 70:
                                return "C"
                            elif score >= 60:
                                return "D"
                            else:
                                return "F"
                        
                        # Create overall performance dataframe
                        # Merge test data with student names
                        test1_with_names = pd.merge(test1_df, student_info, on='Student ID')
                        surprise_with_names = pd.merge(surprise_df, student_info, on='Student ID')
                        test2_with_names = pd.merge(test2_df, student_info, on='Student ID')
                        unit_with_names = pd.merge(unit_df, student_info, on='Student ID')
                        
                        # Calculate overall average for each student
                        overall_with_names = pd.DataFrame({
                            "Student ID": test1_with_names["Student ID"],
                            "Name": test1_with_names["Name"],
                            "Test 1 Average (%)": test1_avg_pct,
                            "Surprise Test Average (%)": surprise_avg_pct,
                            "Test 2 Average (%)": test2_avg_pct,
                            "Unit Test Average (%)": unit_avg_pct
                        })
                        
                        # Calculate overall average across all tests
                        overall_with_names["Overall Average (%)"] = overall_with_names[["Test 1 Average (%)", "Surprise Test Average (%)", 
                                                                                "Test 2 Average (%)", "Unit Test Average (%)"]].mean(axis=1)
                        
                        # Add grades to overall dataframe
                        overall_with_names["Grade"] = overall_with_names["Overall Average (%)"].apply(assign_grade)
                        
                        # Create grade distribution chart
                        grade_counts = overall_with_names["Grade"].value_counts().reset_index()
                        grade_counts.columns = ["Grade", "Count"]
                        
                        # Sort grades in correct order
                        grade_order = {"A": 1, "B": 2, "C": 3, "D": 4, "F": 5}
                        grade_counts["Order"] = grade_counts["Grade"].map(grade_order)
                        grade_counts = grade_counts.sort_values("Order")
                        
                        fig = px.bar(
                            grade_counts,
                            x="Grade",
                            y="Count",
                            color="Grade",
                            text="Count",
                            title="Overall Grade Distribution",
                            color_discrete_map={
                                "A": "green",
                                "B": "lightgreen",
                                "C": "yellow",
                                "D": "orange",
                                "F": "red"
                            }
                        )
                        fig.update_layout(
                            xaxis_title="Grade",
                            yaxis_title="Number of Students"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Could not load all test data. Please check the Excel file.")
            
    # Contact Information Page
    elif page == "Contact Information":
        st.header("Contact Information")
        
        st.subheader("School Contact Details")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""### School Address
            123 Education Street  
            Knowledge City, KN 12345  
            India
            """)
        
        with col2:
            st.markdown("""### Contact Numbers
            **Phone:** +91 1234567890  
            **Fax:** +91 1234567891  
            **Email:** info@schoolname.edu
            """)
        
        st.subheader("Faculty Contact Information")
        
        # Create a sample faculty dataframe
        faculty_data = {
            "Name": ["Dr. Rajesh Kumar", "Mrs. Priya Sharma", "Mr. Amit Patel", "Ms. Deepa Gupta", "Mr. Sanjay Verma"],
            "Subject": ["Mathematics", "English", "Science", "Social Studies", "Languages"],
            "Email": ["rajesh.kumar@schoolname.edu", "priya.sharma@schoolname.edu", 
                        "amit.patel@schoolname.edu", "deepa.gupta@schoolname.edu", "sanjay.verma@schoolname.edu"],
            "Office Hours": ["Mon-Wed: 9AM-11AM", "Tue-Thu: 10AM-12PM", "Wed-Fri: 1PM-3PM", 
                            "Mon-Fri: 11AM-1PM", "Tue-Thu: 2PM-4PM"]
        }
        
        faculty_df = pd.DataFrame(faculty_data)
        st.dataframe(faculty_df, use_container_width=True)
        
        st.subheader("Send a Message")
        
        # Create a contact form
        contact_form_col1, contact_form_col2 = st.columns(2)
        
        with contact_form_col1:
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            recipient = st.selectbox("Send To", faculty_df["Name"].tolist() + ["Administration"])
        
        with contact_form_col2:
            subject = st.text_input("Subject")
            message = st.text_area("Message", height=150)
        
        if st.button("Send Message"):
            if name and email and subject and message:
                st.success("Your message has been sent! We will get back to you soon.")
            else:
                st.warning("Please fill in all fields before sending.")
        
        st.subheader("Visit Us")
        st.markdown("""Feel free to visit our campus during working hours:  
        **Monday to Friday:** 8:00 AM to 4:00 PM  
        **Saturday:** 8:00 AM to 12:00 PM  
        **Sunday:** Closed""")
        
        # Add a map placeholder
        st.image("https://via.placeholder.com/800x400?text=School+Location+Map", caption="School Location Map")

# Run the application
if __name__ == "__main__":
    main()