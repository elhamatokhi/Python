"""
Product Pricing Manager
Reads product data from a file, applies category and tier discounts,
and generates a formatted pricing report.
"""

import logging
import os

logging.basicConfig(
    level=logging.INFO,
format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Discount configuration: category -> discount percentage
CATEGORY_DISCOUNTS = {
    "Electronics": 10,
    "Clothing": 15,
    "Books": 5,
    "Home": 12,
}

# Tier -> additional discount percentage
TIER_DISCOUNTS = {
    "Premium": 5,
    "Standard": 0,
    "Budget": 2,
}

INPUT_FILE = "products.txt"
OUTPUT_FILE = "pricing_report.txt"


def read_products(filepath: str) -> list[dict]:
    """
    Read product data from file. Each line: ProductName,BasePrice,Category,DiscountTier.
    Returns list of dicts with keys: name, base_price, category, tier.
    """
    products = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 4:
                raise ValueError(
                    f"Line {line_num}: expected 4 fields (ProductName,BasePrice,Category,DiscountTier), got {len(parts)}"
                )
            name, base_price_str, category, tier = parts
            try:
                base_price = float(base_price_str)
            except ValueError:
                raise ValueError(
                    f"Line {line_num}: invalid price '{base_price_str}' for product '{name}'"
                )
            if base_price < 0:
                raise ValueError(
                    f"Line {line_num}: price must be non-negative for product '{name}'"
                )
            category_pct = CATEGORY_DISCOUNTS.get(category)
            tier_pct = TIER_DISCOUNTS.get(tier)
            if category_pct is None:
                raise ValueError(
                    f"Line {line_num}: unknown category '{category}' for product '{name}'"
                )
            if tier_pct is None:
                raise ValueError(
                    f"Line {line_num}: unknown tier '{tier}' for product '{name}'"
                )
            products.append({
                "name": name,
                "base_price": base_price,
                "category": category,
                "tier": tier,
            })
    return products


def calculate_pricing(product: dict) -> dict:
    """Apply category and tier discounts; return product with discount_pct, discount_amount, final_price."""
    base = product["base_price"]
    category_pct = CATEGORY_DISCOUNTS[product["category"]]
    tier_pct = TIER_DISCOUNTS[product["tier"]]
    total_discount_pct = category_pct + tier_pct
    discount_amount = round(base * (total_discount_pct / 100), 2)
    final_price = round(base - discount_amount, 2)
    return {
        **product,
        "discount_pct": total_discount_pct,
        "discount_amount": discount_amount,
        "final_price": final_price,
    }


def generate_report(priced_products: list[dict], filepath: str) -> None:
    """Write pricing_report.txt with header and aligned columns."""
    col_name = "Product Name"
    col_base = "Base Price"
    col_discount_pct = "Total Discount %"
    col_discount_amt = "Discount Amount"
    col_final = "Final Price"

    max_name_len = max(len(col_name), max(len(p["name"]) for p in priced_products), 20)
    width_name = max_name_len + 2
    width_pct = 10
    width_money = 12

    sep_len = width_name + width_pct + 3 * width_money + 6
    lines = [
        "=" * sep_len,
        "                    PRICING REPORT",
        "=" * sep_len,
        "",
        f"{col_name:<{width_name}} {col_base:>{width_money}} {col_discount_pct:>{width_pct}} {col_discount_amt:>{width_money}} {col_final:>{width_money}}",
        "-" * sep_len,
    ]

    for p in priced_products:
        lines.append(
            f"{p['name']:<{width_name}} ${p['base_price']:>{width_money - 1}.2f} {p['discount_pct']:>{width_pct - 1}.1f}% ${p['discount_amount']:>{width_money - 1}.2f} ${p['final_price']:>{width_money - 1}.2f}"
        )

    lines.append("")
    lines.append("=" * sep_len)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, INPUT_FILE)
    output_path = os.path.join(script_dir, OUTPUT_FILE)

    try:
        products = read_products(input_path)
    except FileNotFoundError:
        logger.error("Could not find file '%s'.", input_path)
        return
    except ValueError as e:
        logger.error("Error parsing product data: %s", e)
        return

    if not products:
        logger.warning("No products found in the input file.")
        return

    priced_products = [calculate_pricing(p) for p in products]

    try:
        generate_report(priced_products, output_path)
    except PermissionError:
        logger.error("No permission to write to '%s'.", output_path)
        return
    except OSError as e:
        logger.error("Error writing report: %s", e)
        return

    total_products = len(priced_products)
    avg_discount = sum(p["discount_pct"] for p in priced_products) / total_products

    logger.info("Report written to: %s", output_path)
    logger.info("Total products processed: %d", total_products)
    logger.info("Average discount applied: %.1f%%", avg_discount)


if __name__ == "__main__":
    main()
