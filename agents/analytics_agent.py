import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any
from .agent_base import BaseAgent, AgentType
import os

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class AnalyticsAgent(BaseAgent):
    """Agent responsible for analytics and visualizations"""
    
    def __init__(self, output_dir: str = "outputs"):
        super().__init__("AnalyticsAgent", AgentType.ANALYTICS)
        self.output_dir = output_dir
        self.capabilities = [
            "yearly_kpi_summary",
            "top_performers",
            "correlation_analysis",
            "trend_analysis",
            "create_visualizations"
        ]
        os.makedirs(output_dir, exist_ok=True)
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process analytics tasks"""
        action = task.get("action")
        params = task.get("parameters", {})
        df = params.get("dataframe")
        
        try:
            if action == "yearly_kpi_summary":
                return self.yearly_kpi_summary(df)
            elif action == "top_performers":
                return self.yearly_top_performers(df, params.get("year"))
            elif action == "correlation_analysis":
                return self.correlation_analysis(df, params.get("year"))
            elif action == "trend_analysis":
                return self.trend_analysis(df, params.get("year"))
            elif action == "full_analysis":
                return self.full_analysis(df)
            else:
                return {"error": f"Unknown action: {action}", "success": False}
        except Exception as e:
            self.log(f"Error in analytics: {str(e)}", "ERROR")
            return {"error": str(e), "success": False}
    
    def yearly_kpi_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate yearly KPI summary"""
        self.log("Generating yearly KPI summary...")
        
        summary = (df.groupby('Year')
            .agg(Revenue=('Revenue', 'sum'),
                 Profit=('Profit', 'sum'),
                 Cost=('Cost', 'sum'),
                 Order_Quantity=('Order_Quantity', 'sum'),
                 Unique_Customers=('Customer_ID', 'nunique'))
            .reset_index())
        
        summary['Profit_Margin_%'] = (summary['Profit'] / summary['Revenue'] * 100).round(2)
        summary['Avg_Order_Value'] = df.groupby('Year')['Revenue'].mean().values
        
        # Save summary
        summary_path = os.path.join(self.output_dir, 'yearly_kpi_summary.csv')
        summary.to_csv(summary_path, index=False)
        
        # Create visualizations
        # Revenue chart
        plt.figure(figsize=(10, 5))
        sns.barplot(data=summary, x='Year', y='Revenue')
        plt.title('Total Revenue per Year')
        plt.tight_layout()
        revenue_chart = os.path.join(self.output_dir, 'revenue_by_year.png')
        plt.savefig(revenue_chart, dpi=300)
        plt.close()
        
        # Profit margin chart
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=summary, x='Year', y='Profit_Margin_%', marker='o')
        plt.title('Yearly Profit Margin (%)')
        plt.tight_layout()
        margin_chart = os.path.join(self.output_dir, 'profit_margin_by_year.png')
        plt.savefig(margin_chart, dpi=300)
        plt.close()
        
        return {
            "success": True,
            "summary": summary.to_dict('records'),
            "files": [summary_path, revenue_chart, margin_chart]
        }
    
    def yearly_top_performers(self, df: pd.DataFrame, year: int = None) -> Dict[str, Any]:
        """Analyze top performers"""
        self.log(f"Analyzing top performers for year: {year or 'all'}...")
        
        years = [year] if year else sorted(df['Year'].dropna().unique().tolist())
        all_tops = {}
        files = []
        
        for y in years:
            d = df[df['Year'] == y]
            if d.empty:
                continue
            
            top_products = d.groupby('Product')['Revenue'].sum().nlargest(5)
            
            # Save chart
            plt.figure(figsize=(8, 4))
            sns.barplot(x=top_products.values, y=top_products.index)
            plt.xlabel('Revenue')
            plt.ylabel('Product')
            plt.title(f'Top 5 Products - {y}')
            plt.tight_layout()
            chart_path = os.path.join(self.output_dir, f'top_products_{y}.png')
            plt.savefig(chart_path, dpi=300)
            plt.close()
            
            all_tops[str(y)] = top_products.to_dict()
            files.append(chart_path)
        
        return {
            "success": True,
            "top_products_by_year": all_tops,
            "files": files
        }
    
    def correlation_analysis(self, df: pd.DataFrame, year: int = None) -> Dict[str, Any]:
        """Generate correlation heatmaps"""
        self.log(f"Creating correlation analysis for year: {year or 'all'}...")
        
        years = [year] if year else sorted(df['Year'].dropna().unique().tolist())
        num_cols = [c for c in ['Order_Quantity', 'Unit_Cost', 'Unit_Price',
                                 'Profit', 'Cost', 'Revenue', 'Profit_Margin',
                                 'Customer_Age'] if c in df.columns]
        files = []
        
        for y in years:
            d = df[df['Year'] == y]
            if d.empty or len(num_cols) < 3:
                continue
            
            corr = d[num_cols].corr()
            plt.figure(figsize=(8, 6))
            sns.heatmap(corr, cmap='RdBu', center=0, annot=True, fmt='.2f')
            plt.title(f'Correlation Heatmap ({y})')
            plt.tight_layout()
            chart_path = os.path.join(self.output_dir, f'correlation_heatmap_{y}.png')
            plt.savefig(chart_path, dpi=300)
            plt.close()
            files.append(chart_path)
        
        return {"success": True, "files": files}
    
    def trend_analysis(self, df: pd.DataFrame, year: int = None) -> Dict[str, Any]:
        """Analyze trends"""
        self.log(f"Analyzing trends for year: {year or 'all'}...")
        
        years = [year] if year else sorted(df['Year'].dropna().unique().tolist())
        files = []
        
        for y in years:
            d = df[df['Year'] == y]
            if d.empty:
                continue
            
            monthly = (d.groupby('Month_Year')
                .agg(Revenue=('Revenue', 'sum'), Profit=('Profit', 'sum'))
                .reset_index().sort_values('Month_Year'))
            
            plt.figure(figsize=(10, 5))
            sns.lineplot(data=monthly, x='Month_Year', y='Revenue', label='Revenue')
            sns.lineplot(data=monthly, x='Month_Year', y='Profit', label='Profit')
            plt.xticks(rotation=45)
            plt.title(f'Monthly Revenue vs Profit ({y})')
            plt.tight_layout()
            chart_path = os.path.join(self.output_dir, f'monthly_trend_{y}.png')
            plt.savefig(chart_path, dpi=300)
            plt.close()
            files.append(chart_path)
        
        return {"success": True, "files": files}
    
    def full_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run full analysis"""
        self.log("Running full analysis...")
        
        results = {}
        results['kpi_summary'] = self.yearly_kpi_summary(df)
        results['top_performers'] = self.yearly_top_performers(df)
        results['correlations'] = self.correlation_analysis(df)
        results['trends'] = self.trend_analysis(df)
        
        return {
            "success": True,
            "message": "Full analysis completed",
            "results": results
        }