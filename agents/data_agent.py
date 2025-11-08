import pandas as pd
import numpy as np
from typing import Dict, Any
from .agent_base import BaseAgent, AgentType

class DataAgent(BaseAgent):
    """Agent responsible for data loading, cleaning, and feature engineering"""
    
    def __init__(self, data_path: str = None):
        super().__init__("DataAgent", AgentType.DATA)
        self.data_path = data_path
        self.df = None
        self.processed_data = {}
        self.capabilities = [
            "load_data",
            "clean_data",
            "engineer_features",
            "create_specialized_datasets",
            "query_data"
        ]
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process data-related tasks"""
        action = task.get("action")
        params = task.get("parameters", {})
        
        try:
            if action == "load_and_prepare":
                return self.load_and_prepare_data(params.get("file_path"))
            elif action == "query_data":
                return self.query_data(params)
            elif action == "get_summary":
                return self.get_data_summary(params)
            else:
                return {"error": f"Unknown action: {action}", "success": False}
        except Exception as e:
            self.log(f"Error processing task: {str(e)}", "ERROR")
            return {"error": str(e), "success": False}
    
    def load_and_prepare_data(self, file_path: str) -> Dict[str, Any]:
        """Load and prepare all datasets"""
        self.log("Loading data...")
        self.df = pd.read_csv(file_path, low_memory=False)
        
        self.log("Cleaning data...")
        self.df = self._clean_data(self.df)
        
        self.log("Engineering features...")
        self.df = self._engineer_features(self.df)
        
        self.log("Creating specialized datasets...")
        self._create_specialized_datasets()
        
        return {
            "success": True,
            "message": "Data loaded and prepared successfully",
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "date_range": {
                "start": str(self.df['Date'].min()),
                "end": str(self.df['Date'].max())
            }
        }
    
    def _clean_data(self, df):
        """Clean data (from your preprocessing code)"""
        df_clean = df.copy()
        df_clean['Date'] = pd.to_datetime(df_clean['Date'], format='%d/%m/%Y', errors='coerce')
        
        # Fill NA
        for col in df_clean.select_dtypes(include=[np.number]).columns:
            if df_clean[col].isnull().any():
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
        
        for col in df_clean.select_dtypes(include=['object']).columns:
            if df_clean[col].isnull().any():
                df_clean[col] = df_clean[col].fillna(df_clean[col].mode().iloc[0])
        
        df_clean = df_clean.drop_duplicates()
        
        # Optimize dtypes
        dtype_map = {'Day':'int8', 'Year':'int16', 'Customer_Age':'int8', 'Order_Quantity':'int16'}
        for col, dtype in dtype_map.items():
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(dtype)
        
        cats = ['Month','Age_Group','Customer_Gender','Country','State',
                'Product_Category','Sub_Category','Product']
        for col in cats:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype('category')
        
        return df_clean
    
    def _engineer_features(self, df):
        """Engineer features (from your preprocessing code)"""
        df = df.copy()
        
        # Temporal features
        df['Quarter'] = df['Date'].dt.quarter
        df['Week_of_Year'] = df['Date'].dt.isocalendar().week
        df['Day_of_Week'] = df['Date'].dt.dayofweek
        df['Day_Name'] = df['Date'].dt.day_name()
        df['Is_Weekend'] = df['Day_of_Week'].isin([5,6]).astype(int)
        df['Month_Year'] = df['Date'].dt.to_period('M').astype(str)
        
        # Financial metrics
        df['Profit_Margin'] = (df['Profit'] / df['Revenue']) * 100
        df['Markup_Percentage'] = ((df['Unit_Price'] - df['Unit_Cost']) / df['Unit_Cost']) * 100
        df['Revenue_per_Unit'] = df['Revenue'] / df['Order_Quantity']
        df['Profit_per_Unit'] = df['Profit'] / df['Order_Quantity']
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Customer ID and RFM
        df['Customer_ID'] = (df['Customer_Age'].astype(str) + '_' +
                            df['Customer_Gender'].astype(str) + '_' +
                            df['Country'].astype(str) + '_' +
                            df['State'].astype(str))
        
        latest = df['Date'].max()
        rfm = df.groupby('Customer_ID').agg(
            Recency_Days=('Date', lambda x: (latest - x.max()).days),
            Frequency=('Revenue', 'count'),
            Monetary_Value=('Revenue', 'sum')
        ).reset_index()
        df = df.merge(rfm, on='Customer_ID', how='left')
        
        return df
    
    def _create_specialized_datasets(self):
        """Create specialized datasets"""
        # Sales dataset
        self.processed_data['sales'] = self.df[[
            'Date', 'Year', 'Month', 'Quarter', 'Product_Category',
            'Sub_Category', 'Product', 'Country', 'State',
            'Order_Quantity', 'Revenue', 'Cost', 'Profit', 'Month_Year'
        ]].copy()
        
        # Customer dataset
        self.processed_data['customer'] = (
            self.df.groupby('Customer_ID')
            .agg(
                Customer_Age=('Customer_Age', 'first'),
                Customer_Gender=('Customer_Gender', 'first'),
                Country=('Country', 'first'),
                State=('State', 'first'),
                Total_Revenue=('Revenue', 'sum'),
                Total_Orders=('Revenue', 'count'),
                Total_Profit=('Profit', 'sum'),
                Avg_Order_Value=('Revenue', 'mean'),
                Recency_Days=('Recency_Days', 'first'),
                Frequency=('Frequency', 'first'),
                Monetary_Value=('Monetary_Value', 'first')
            ).reset_index()
        )
        
        # Profit dataset
        self.processed_data['profit'] = self.df[[
            'Date', 'Month_Year', 'Product_Category', 'Sub_Category',
            'Product', 'Country', 'State', 'Revenue', 'Cost', 'Profit',
            'Profit_Margin', 'Unit_Cost', 'Unit_Price'
        ]].copy()
    
    def query_data(self, params: Dict) -> Dict[str, Any]:
        """Query data based on parameters"""
        query_type = params.get("query_type")
        
        if query_type == "profit_margin_by_year":
            year = params.get("year")
            return self._get_profit_margin_by_year(year)
        
        elif query_type == "revenue_trends":
            start_year = params.get("start_year")
            end_year = params.get("end_year")
            return self._get_revenue_trends(start_year, end_year)
        
        elif query_type == "top_products":
            year = params.get("year")
            limit = params.get("limit", 5)
            return self._get_top_products(year, limit)
        
        elif query_type == "customer_analysis":
            return self._get_customer_analysis(params)
        
        else:
            return {"error": f"Unknown query type: {query_type}"}
    
    def _get_profit_margin_by_year(self, year: int) -> Dict[str, Any]:
        """Get profit margin for a specific year"""
        if self.df is None:
            return {"error": "Data not loaded"}
        
        year_data = self.df[self.df['Year'] == year]
        
        if year_data.empty:
            return {
                "error": f"No data found for year {year}",
                "available_years": sorted(self.df['Year'].unique().tolist())
            }
        
        total_revenue = year_data['Revenue'].sum()
        total_profit = year_data['Profit'].sum()
        total_cost = year_data['Cost'].sum()
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            "success": True,
            "year": int(year),
            "revenue": float(total_revenue),
            "profit": float(total_profit),
            "cost": float(total_cost),
            "profit_margin": round(float(profit_margin), 2),
            "total_orders": int(len(year_data)),
            "unique_customers": int(year_data['Customer_ID'].nunique())
        }
    
    def _get_revenue_trends(self, start_year: int = None, end_year: int = None) -> Dict[str, Any]:
        """Get revenue trends over years"""
        if self.df is None:
            return {"error": "Data not loaded"}
        
        df_filtered = self.df.copy()
        
        if start_year:
            df_filtered = df_filtered[df_filtered['Year'] >= start_year]
        if end_year:
            df_filtered = df_filtered[df_filtered['Year'] <= end_year]
        
        yearly_summary = (
            df_filtered.groupby('Year')
            .agg(
                Revenue=('Revenue', 'sum'),
                Profit=('Profit', 'sum'),
                Orders=('Order_Quantity', 'sum'),
                Customers=('Customer_ID', 'nunique')
            )
            .reset_index()
        )
        
        yearly_summary['Profit_Margin'] = (
            yearly_summary['Profit'] / yearly_summary['Revenue'] * 100
        ).round(2)
        
        # Calculate year-over-year growth
        yearly_summary['Revenue_Growth_%'] = yearly_summary['Revenue'].pct_change() * 100
        yearly_summary['Revenue_Growth_%'] = yearly_summary['Revenue_Growth_%'].round(2)
        
        return {
            "success": True,
            "trends": yearly_summary.to_dict('records')
        }
    
    def _get_top_products(self, year: int = None, limit: int = 5) -> Dict[str, Any]:
        """Get top performing products"""
        if self.df is None:
            return {"error": "Data not loaded"}
        
        df_filtered = self.df.copy()
        if year:
            df_filtered = df_filtered[df_filtered['Year'] == year]
        
        top_products = (
            df_filtered.groupby('Product')
            .agg(
                Revenue=('Revenue', 'sum'),
                Profit=('Profit', 'sum'),
                Orders=('Order_Quantity', 'sum')
            )
            .sort_values('Revenue', ascending=False)
            .head(limit)
            .reset_index()
        )
        
        return {
            "success": True,
            "year": year if year else "all",
            "top_products": top_products.to_dict('records')
        }
    
    def _get_customer_analysis(self, params: Dict) -> Dict[str, Any]:
        """Get customer analysis"""
        if 'customer' not in self.processed_data:
            return {"error": "Customer data not available"}
        
        customer_df = self.processed_data['customer']
        
        summary = {
            "total_customers": int(len(customer_df)),
            "total_revenue": float(customer_df['Total_Revenue'].sum()),
            "avg_customer_value": float(customer_df['Total_Revenue'].mean()),
            "avg_orders_per_customer": float(customer_df['Total_Orders'].mean()),
            "top_customers": customer_df.nlargest(5, 'Total_Revenue')[
                ['Customer_ID', 'Total_Revenue', 'Total_Orders']
            ].to_dict('records')
        }
        
        return {"success": True, **summary}
    
    def get_data_summary(self, params: Dict) -> Dict[str, Any]:
        """Get overall data summary"""
        if self.df is None:
            return {"error": "Data not loaded"}
        
        return {
            "success": True,
            "total_records": int(len(self.df)),
            "date_range": {
                "start": str(self.df['Date'].min()),
                "end": str(self.df['Date'].max())
            },
            "years_available": sorted(self.df['Year'].unique().tolist()),
            "total_revenue": float(self.df['Revenue'].sum()),
            "total_profit": float(self.df['Profit'].sum()),
            "unique_products": int(self.df['Product'].nunique()),
            "unique_customers": int(self.df['Customer_ID'].nunique()),
            "countries": self.df['Country'].unique().tolist()
        }