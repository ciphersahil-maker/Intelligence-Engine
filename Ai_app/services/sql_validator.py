# FORBIDDEN = [
#     "DROP",
#     "DELETE",
#     "UPDATE",
#     "INSERT",
#     "ALTER",
#     "TRUNCATE"
# ]

# def validate_sql(sql):

#     sql_upper = sql.upper()

#     for word in FORBIDDEN:
#         if word in sql_upper:
#             raise Exception("Unsafe SQL detected")

#     if not sql_upper.startswith("SELECT"):
#         raise Exception("Only SELECT queries allowed")

#     return True
# -------------------------old code-------------------------



import re

FORBIDDEN = [
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"
]

def validate_sql(sql):
    sql_upper = sql.upper()

    for word in FORBIDDEN:
        if word in sql_upper:
            raise Exception("Unsafe SQL detected")

    if "INFORMATION_SCHEMA" in sql_upper:
        raise Exception("Access denied")

    if not sql_upper.startswith("SELECT"):
        raise Exception("Only SELECT queries allowed")

    return True


def validate_columns(sql, schema):
    import re

    valid_columns = [col.split(" ")[0] for col in schema.split("\n") if "(" in col]

    # remove string values
    sql_clean = re.sub(r"'[^']*'", "", sql.lower())

    # extract aliases
    aliases = re.findall(r"\bas\s+([a-z_]+)", sql_clean)

    words = re.findall(r"\b[a-z_]+\b", sql_clean)

    ignore = {
        "select","from","where","and","or","group","by","order","limit",
        "desc","asc","as","between","like","in","is","null"
    }

    functions = {
        "sum", "count", "avg", "min", "max",
        "extract", "coalesce", "case", "when", "then", "else", "end",
        "date_part", "interval"
    }


    keywords = {
        "interval","epoch","distinct","case","when","then","else","end"
    }

    ignore_all = ignore.union(functions).union(keywords)

    for word in words:
        if word in ignore_all:
            continue
        if word in aliases:
            continue
        if word not in valid_columns and word != "booking":
            raise Exception(f"Invalid column detected: {word}")