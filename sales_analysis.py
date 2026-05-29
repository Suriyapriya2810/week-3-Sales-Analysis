import os
import pandas as pd
def load_data(file_path):
    """Loads the CSV dataset securely and checks if the file exists."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Error: '{file_path}' not found. Please ensure it is in the working directory."
        )

    print(f"🔄 Loading dataset: {file_path}...")
    return pd.read_csv(file_path)


def clean_data(df):
    """Handles missing data across numerical and categorical columns systematically."""
    print("🧹 Cleaning data and handling missing values...")

    # Create a copy to prevent Setting With Copy Warning
    df_clean = df.copy()

    # --- HANDLING MISSING DATA ---
    # 1. Fill missing numeric sales values with 0 so calculations don't break
    if "Total_Sales" in df_clean.columns:
        df_clean["Total_Sales"] = df_clean["Total_Sales"].fillna(0)

    # 2. Fill missing categorical values with 'Unknown' to prevent drop-out during grouping
    if "Product" in df_clean.columns:
        df_clean["Product"] = (
            df_clean["Product"].fillna("Unknown Product").str.strip()
        )

    if "Region" in df_clean.columns:
        df_clean["Region"] = (
            df_clean["Region"].fillna("Unknown Region").str.strip()
        )

    return df_clean


def calculate_metrics(df):
    """Calculates all mandatory and advanced regional/product sales metrics."""
    metrics = {}

    # Metric 1: Total Overall Revenue
    metrics["total_revenue"] = df["Total_Sales"].sum()

    # Metric 2: Top 3 Selling Products Globally
    if "Product" in df.columns:
        metrics["top_3_products"] = (
            df.groupby("Product")["Total_Sales"].sum().nlargest(3)
        )
    else:
        metrics["top_3_products"] = None

    # Metric 3: Total Sales Revenue for Each Region
    if "Region" in df.columns:
        metrics["region_revenue"] = df.groupby("Region")["Total_Sales"].sum()
        metrics["highest_region_name"] = metrics["region_revenue"].idxmax()
        metrics["highest_region_sales"] = metrics["region_revenue"].max()
    else:
        metrics["region_revenue"] = None

    # Metric 4: Total Sales of Each Product in Each Region (Cross-tabulation matrix)
    if "Region" in df.columns and "Product" in df.columns:
        # Using pivot_table to generate a clean Product vs Region sales matrix
        metrics["product_by_region"] = df.pivot_table(
            index="Product",
            columns="Region",
            values="Total_Sales",
            aggfunc="sum",
        ).fillna(0)

        # Metric 5: Highest Selling Product in Each Region
        # Group by Region and Product, calculate sums, then locate the max product per region
        region_product_totals = df.groupby(["Region", "Product"])[
            "Total_Sales"
        ].sum()
        highest_prod_per_region = {}

        for region in df["Region"].unique():
            try:
                # Isolate the specific region's product metrics
                region_data = region_product_totals.loc[region]
                top_product = region_data.idxmax()
                top_sales = region_data.max()
                highest_prod_per_region[region] = (top_product, top_sales)
            except KeyError:
                continue
        metrics["highest_product_per_region"] = highest_prod_per_region
    else:
        metrics["product_by_region"] = None
        metrics["highest_product_per_region"] = None

    return metrics


def display_report(metrics):
    """Prints a perfectly structured final report matching professional standards."""
    print("\n" + "=" * 60)
    print("         💥 EXTENSIVE SALES DATA ANALYSIS REPORT 💥        ")
    print("=" * 60)

    # 1. High-Level Summary
    print(f"📈 Total Overall Revenue  : ₹{metrics['total_revenue']:,.2f}")
    if metrics["region_revenue"] is not None:
        print(
            f"🌍 Highest Selling Region : {metrics['highest_region_name']} (₹{metrics['highest_region_sales']:,.2f})"
        )

    # 2. Top 3 Global Products
    print("\n🏆 Top 3 Selling Products Globally:")
    if metrics["top_3_products"] is not None:
        for idx, (product, sales) in enumerate(
            metrics["top_3_products"].items(), 1
        ):
            print(f"   {idx}. {product:<22} : ₹{sales:,.2f}")

    # 3. Total Sales Revenue for Each Region
    print("\n🗺️ Total Sales Revenue by Region:")
    if metrics["region_revenue"] is not None:
        for region, revenue in metrics["region_revenue"].items():
            print(f"   📍 {region:<23} : ₹{revenue:,.2f}")

    # 4. Highest Selling Product in Each Region
    print("\n⭐ Highest Selling Product in Each Region:")
    if metrics["highest_product_per_region"] is not None:
        for region, (product, sales) in metrics[
            "highest_product_per_region"
        ].items():
            print(
                f"   ▪️ In {region:<15} -> Top Product: {product:<15} (₹{sales:,.2f})"
            )

    # 5. Comprehensive Breakdown Matrix
    print("\n📊 Total Sales Matrix (Each Product in Each Region):")
    if metrics["product_by_region"] is not None:
        print("-" * 60)
        # Displaying the clean pandas dataframe format directly inside the report layout
        print(metrics["product_by_region"].map(lambda x: f"₹{x:,.2f}"))
        print("-" * 60)

    print("=" * 60 + "\n")


def main():
    """Main execution pipeline."""
    csv_file = "sales_data.csv"

    try:
        # Run Data Pipeline
        raw_df = load_data(csv_file)
        cleaned_df = clean_data(raw_df)
        sales_metrics = calculate_metrics(cleaned_df)

        # Output Visual Structured Report
        display_report(sales_metrics)

    except Exception as e:
        print(f"\n❌ An error occurred during execution: {e}")


if __name__ == "__main__":
    main()
