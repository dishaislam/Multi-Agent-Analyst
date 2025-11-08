import os
import warnings
from typing import Dict, Any, List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px

from .agent_base import BaseAgent, AgentType

warnings.filterwarnings("ignore")

plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")


class AnalyticsAgent(BaseAgent):
    """Agent responsible for analytics and visualizations (EDA-style)."""

    def __init__(self, output_dir: str = "outputs"):
        super().__init__("AnalyticsAgent", AgentType.ANALYTICS)
        self.output_dir = output_dir
        self.capabilities: List[str] = [
            "yearly_kpi_summary",
            "top_performers",
            "correlation_analysis",
            "trend_analysis",
            "customer_segmentation",
            "generate_yearly_summary_text",
            "full_analysis",
        ]
        os.makedirs(output_dir, exist_ok=True)

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:

        action = task.get("action")
        params = task.get("parameters", {})
        df = params.get("dataframe")
        year = params.get("year")

        if df is None or not isinstance(df, pd.DataFrame):
            return {"success": False, "error": "AnalyticsAgent requires a pandas DataFrame"}

        try:
            if action == "yearly_kpi_summary":
                return self.yearly_kpi_summary(df)
            elif action == "top_performers":
                return self.yearly_top_performers(df, year)
            elif action == "correlation_analysis":
                return self.correlation_analysis(df, year)
            elif action == "trend_analysis":
                return self.trend_analysis(df, year)
            elif action == "customer_segmentation":
                return self.customer_segmentation(df, year)
            elif action == "generate_yearly_summary_text":
                return self.generate_yearly_summary_text(df)
            elif action == "full_analysis":
                return self.full_analysis(df)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            self.log(f"Error in analytics: {e}", level="ERROR")
            return {"success": False, "error": str(e)}

    def _ensure_year(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "Date" in df.columns and "Year" not in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df["Year"] = df["Date"].dt.year
        return df

    def _get_years(self, df: pd.DataFrame, year: int | None) -> List[int]:
        if year is not None:
            return [year]
        return sorted(df["Year"].dropna().unique().tolist())


    def yearly_kpi_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        self.log("Generating yearly KPI summary...")

        df = self._ensure_year(df)

        summary = (
            df.groupby("Year")
            .agg(
                {
                    "Revenue": "sum",
                    "Profit": "sum",
                    "Cost": "sum",
                    "Order_Quantity": "sum",
                    "Customer_ID": "nunique",
                }
            )
            .reset_index()
        )

        summary["Profit_Margin_%"] = (summary["Profit"] / summary["Revenue"]) * 100
        summary["Avg_Order_Value"] = df.groupby("Year")["Revenue"].mean().values

        summary_path = os.path.join(self.output_dir, "yearly_kpi_summary.csv")
        summary.to_csv(summary_path, index=False)

        # Revenue per year
        plt.figure(figsize=(10, 5))
        sns.barplot(x="Year", y="Revenue", data=summary)
        plt.title("Total Revenue per Year")
        plt.tight_layout()
        revenue_chart = os.path.join(self.output_dir, "revenue_by_year.png")
        plt.savefig(revenue_chart, dpi=300)
        plt.close()

        # Profit margin per year
        plt.figure(figsize=(10, 5))
        sns.lineplot(x="Year", y="Profit_Margin_%", data=summary, marker="o")
        plt.title("Yearly Profit Margin (%)")
        plt.tight_layout()
        margin_chart = os.path.join(self.output_dir, "profit_margin_by_year.png")
        plt.savefig(margin_chart, dpi=300)
        plt.close()

        return {
            "success": True,
            "summary": summary.to_dict("records"),
            "files": [summary_path, revenue_chart, margin_chart],
        }

    def yearly_top_performers(
        self, df: pd.DataFrame, year: int | None = None
    ) -> Dict[str, Any]:
        self.log(f"Analyzing top performers for year: {year or 'all'}...")

        df = self._ensure_year(df)
        years = self._get_years(df, year)

        results_by_year: Dict[str, Dict[str, Any]] = {}
        files: List[str] = []

        for y in years:
            d = df[df["Year"] == y]
            if d.empty:
                continue

            top_products = d.groupby("Product")["Revenue"].sum().nlargest(5)

            # Build a small DataFrame so we control the categories explicitly
            plot_df = top_products.reset_index()
            plot_df.columns = ["Product", "Revenue"]

            # Make sure Product is plain text, not a big shared Categorical
            plot_df["Product"] = plot_df["Product"].astype(str)

            plt.figure(figsize=(8, 4))

            sns.barplot(
                data=plot_df,
                x="Revenue",
                y="Product",
                # Only use these 5 labels, in this order
                order=plot_df["Product"].tolist(),
            )

            plt.title(f"Top 5 Products - {y}")
            plt.xlabel("Revenue")
            plt.ylabel("Product")
            plt.tight_layout()

            chart_path = os.path.join(self.output_dir, f"top_products_{y}.png")
            plt.savefig(chart_path, dpi=300)
            plt.close()


        return {"success": True, "results_by_year": results_by_year, "files": files}

    def correlation_analysis(
        self, df: pd.DataFrame, year: int | None = None
    ) -> Dict[str, Any]:
        self.log(f"Creating correlation analysis for year: {year or 'all'}...")

        df = self._ensure_year(df)
        years = self._get_years(df, year)

        num_cols = [
            "Order_Quantity",
            "Unit_Cost",
            "Unit_Price",
            "Profit",
            "Cost",
            "Revenue",
            "Profit_Margin",
            "Customer_Age",
        ]
        num_cols = [c for c in num_cols if c in df.columns]

        files: List[str] = []

        for y in years:
            d = df[df["Year"] == y]
            if d.empty:
                continue

            corr = d[num_cols].corr()
            plt.figure(figsize=(8, 6))
            sns.heatmap(corr, cmap="RdBu", center=0, annot=True, fmt=".2f")
            plt.title(f"Correlation Heatmap ({y})")
            plt.tight_layout()
            chart_path = os.path.join(self.output_dir, f"correlation_heatmap_{y}.png")
            plt.savefig(chart_path, dpi=300)
            plt.close()
            files.append(chart_path)

        return {"success": True, "files": files}


    def trend_analysis(
        self, df: pd.DataFrame, year: int | None = None
    ) -> Dict[str, Any]:
        self.log(f"Analyzing trends for year: {year or 'all'}...")

        df = self._ensure_year(df)

        # ensure Month_Year like in EDA
        if "Month_Year" not in df.columns and "Date" in df.columns:
            df = df.copy()
            df["Month_Year"] = pd.to_datetime(df["Date"], errors="coerce").dt.to_period(
                "M"
            ).astype(str)

        years = self._get_years(df, year)
        files: List[str] = []

        for y in years:
            d = df[df["Year"] == y]
            if d.empty:
                continue

            monthly = (
                d.groupby("Month_Year")
                .agg({"Revenue": "sum", "Profit": "sum"})
                .reset_index()
            )

            plt.figure(figsize=(10, 5))
            sns.lineplot(x="Month_Year", y="Revenue", data=monthly, label="Revenue")
            sns.lineplot(x="Month_Year", y="Profit", data=monthly, label="Profit")
            plt.title(f"Monthly Revenue vs Profit ({y})")
            plt.xticks(rotation=45)
            plt.tight_layout()
            chart_path = os.path.join(self.output_dir, f"monthly_trend_{y}.png")
            plt.savefig(chart_path, dpi=300)
            plt.close()
            files.append(chart_path)

        return {"success": True, "files": files}

    def customer_segmentation(
        self, df: pd.DataFrame, year: int | None = None
    ) -> Dict[str, Any]:
        self.log(f"Generating customer segmentation for year: {year or 'all'}...")

        df = self._ensure_year(df)
        years = self._get_years(df, year)

        files: List[str] = []

        for y in years:
            d = df[df["Year"] == y]
            if d.empty:
                continue

            if "Age_Group" in d.columns and "Customer_Gender" in d.columns:
                seg = (
                    d.groupby(["Age_Group", "Customer_Gender"])["Revenue"]
                    .sum()
                    .reset_index()
                )
                fig = px.sunburst(
                    seg,
                    path=["Age_Group", "Customer_Gender"],
                    values="Revenue",
                    title=f"Customer Segmentation ({y})",
                    color="Revenue",
                    color_continuous_scale="Blues",
                )
                chart_path = os.path.join(
                    self.output_dir, f"customer_segmentation_{y}.png"
                )
                # requires kaleido installed – same as EDA.py
                fig.write_image(chart_path, engine="kaleido")
                files.append(chart_path)

        return {"success": True, "files": files}


    def generate_yearly_summary_text(self, df: pd.DataFrame) -> Dict[str, Any]:
        self.log("Generating yearly insights text summary...")

        df = self._ensure_year(df)

        summary = (
            df.groupby("Year")
            .agg(
                {
                    "Revenue": "sum",
                    "Profit": "sum",
                    "Cost": "sum",
                    "Order_Quantity": "sum",
                    "Customer_ID": "nunique",
                }
            )
            .reset_index()
        )

        summary["Profit_Margin_%"] = (summary["Profit"] / summary["Revenue"]) * 100

        years = sorted(summary["Year"].unique())
        text = "YEARLY INSIGHTS SUMMARY\n" + "=" * 80 + "\n\n"

        for y in years:
            ydata = summary[summary["Year"] == y].iloc[0]
            text += f"📅 YEAR: {y}\n"
            text += f"→ Total Revenue: ${float(ydata['Revenue']):,.2f}\n"
            text += f"→ Total Profit: ${float(ydata['Profit']):,.2f}\n"
            text += f"→ Profit Margin: {float(ydata['Profit_Margin_%']):.2f}%\n"
            text += f"→ Unique Customers: {int(ydata['Customer_ID']):,}\n"
            text += "-" * 60 + "\n"

        path = os.path.join(self.output_dir, "yearly_insights_summary.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

        return {"success": True, "file": path, "text_preview": text[:500]}


    def full_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        self.log("Running full EDA-style analysis...")

        kpi = self.yearly_kpi_summary(df)
        tops = self.yearly_top_performers(df)
        corr = self.correlation_analysis(df)
        trends = self.trend_analysis(df)
        seg = self.customer_segmentation(df)
        summary_txt = self.generate_yearly_summary_text(df)

        return {
            "success": True,
            "message": "Full analysis completed (EDA-style)",
            "results": {
                "kpi_summary": kpi,
                "top_performers": tops,
                "correlations": corr,
                "trends": trends,
                "customer_segmentation": seg,
                "yearly_summary_text": summary_txt,
            },
        }
