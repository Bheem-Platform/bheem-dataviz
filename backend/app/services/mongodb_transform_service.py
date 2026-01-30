"""
MongoDB Transform Service - Aggregation Pipeline Generator.

Converts transform recipe steps into MongoDB aggregation pipelines.
"""

from typing import List, Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)


class MongoDBTransformService:
    """
    Service for generating MongoDB aggregation pipelines from transform steps.
    """

    def generate_pipeline(
        self,
        steps: List[Dict[str, Any]],
        limit: Optional[int] = None,
        skip: int = 0,
        available_columns: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate MongoDB aggregation pipeline from transform steps.

        Args:
            steps: List of transform step configurations
            limit: Optional row limit
            skip: Number of documents to skip
            available_columns: List of available field names

        Returns:
            MongoDB aggregation pipeline (list of stages)
        """
        pipeline = []

        # Track state
        selected_columns = None  # None means all columns
        column_renames = {}  # {old_name: new_name}
        dropped_columns = set()
        added_fields = {}  # {field_name: expression}

        for step in steps:
            step_type = step.get("type")

            if step_type == "select":
                selected_columns = step.get("columns", [])

            elif step_type == "rename":
                mapping = step.get("mapping", {})
                column_renames.update(mapping)

            elif step_type == "drop_column":
                cols = step.get("columns", [])
                dropped_columns.update(cols)

            elif step_type == "add_column":
                name = step.get("name")
                expression = step.get("expression")
                if name and expression:
                    # Parse expression to MongoDB format
                    mongo_expr = self._parse_expression(expression)
                    added_fields[name] = mongo_expr

            elif step_type == "filter":
                match_stage = self._build_match_stage(step)
                if match_stage:
                    pipeline.append({"$match": match_stage})

            elif step_type == "sort":
                sort_stage = self._build_sort_stage(step)
                if sort_stage:
                    pipeline.append({"$sort": sort_stage})

            elif step_type == "join":
                lookup_stage = self._build_lookup_stage(step)
                if lookup_stage:
                    pipeline.append(lookup_stage)

            elif step_type == "group_by":
                group_stage = self._build_group_stage(step)
                if group_stage:
                    pipeline.append({"$group": group_stage})

            elif step_type == "deduplicate":
                dedup_stage = self._build_deduplicate_stage(step, available_columns)
                if dedup_stage:
                    pipeline.extend(dedup_stage)

            elif step_type == "fill_null":
                col = step.get("column")
                val = step.get("value")
                if col:
                    added_fields[col] = {"$ifNull": [f"${col}", val]}

            elif step_type == "trim":
                for col in step.get("columns", []):
                    if col:
                        added_fields[col] = {"$trim": {"input": f"${col}"}}

            elif step_type == "case":
                col = step.get("column")
                case_type = step.get("to", "upper")
                if col:
                    if case_type == "upper":
                        added_fields[col] = {"$toUpper": f"${col}"}
                    elif case_type == "lower":
                        added_fields[col] = {"$toLower": f"${col}"}
                    elif case_type == "title":
                        # MongoDB doesn't have built-in title case, use a workaround
                        # This is a simplified version - just capitalize first letter
                        added_fields[col] = {
                            "$concat": [
                                {"$toUpper": {"$substr": [f"${col}", 0, 1]}},
                                {"$toLower": {"$substr": [f"${col}", 1, {"$subtract": [{"$strLenCP": f"${col}"}, 1]}]}}
                            ]
                        }

            elif step_type == "cast":
                col = step.get("column")
                to_type = step.get("to_type", "string").lower()
                if col:
                    added_fields[col] = self._build_cast_expression(col, to_type)

            elif step_type == "replace":
                col = step.get("column")
                find_val = step.get("find")
                replace_val = step.get("replace_with", "")
                if col:
                    if find_val is None or find_val == "NULL":
                        # Replace null values
                        added_fields[col] = {"$ifNull": [f"${col}", replace_val]}
                    else:
                        # Replace string values
                        added_fields[col] = {
                            "$replaceAll": {
                                "input": f"${col}",
                                "find": find_val,
                                "replacement": replace_val
                            }
                        }

        # Apply field transformations via $addFields
        if added_fields:
            pipeline.append({"$addFields": added_fields})

        # Build $project stage for select, rename, drop
        project_stage = self._build_project_stage(
            selected_columns,
            column_renames,
            dropped_columns,
            available_columns
        )
        if project_stage:
            pipeline.append({"$project": project_stage})

        # Add skip and limit
        if skip > 0:
            pipeline.append({"$skip": skip})

        if limit is not None:
            pipeline.append({"$limit": limit})

        return pipeline

    def _build_match_stage(self, step: Dict[str, Any]) -> Optional[Dict]:
        """Build $match stage from filter step."""
        conditions = step.get("conditions", [])
        logic = step.get("logic", "and").lower()

        if not conditions:
            return None

        match_conditions = []

        for cond in conditions:
            col = cond.get("column", "")
            if not col:
                continue

            op = cond.get("operator", "=")
            val = cond.get("value")

            if op == "=" or op == "==":
                match_conditions.append({col: val})
            elif op == "!=":
                match_conditions.append({col: {"$ne": val}})
            elif op == ">":
                match_conditions.append({col: {"$gt": val}})
            elif op == ">=":
                match_conditions.append({col: {"$gte": val}})
            elif op == "<":
                match_conditions.append({col: {"$lt": val}})
            elif op == "<=":
                match_conditions.append({col: {"$lte": val}})
            elif op == "is_null":
                match_conditions.append({col: {"$eq": None}})
            elif op == "is_not_null":
                match_conditions.append({col: {"$ne": None}})
            elif op == "in":
                vals = val if isinstance(val, list) else [val]
                match_conditions.append({col: {"$in": vals}})
            elif op == "not_in":
                vals = val if isinstance(val, list) else [val]
                match_conditions.append({col: {"$nin": vals}})
            elif op == "like":
                # Convert SQL LIKE to regex
                regex = self._like_to_regex(val)
                match_conditions.append({col: {"$regex": regex, "$options": "i"}})
            elif op == "not_like":
                regex = self._like_to_regex(val)
                match_conditions.append({col: {"$not": {"$regex": regex, "$options": "i"}}})
            elif op == "contains":
                match_conditions.append({col: {"$regex": re.escape(str(val)), "$options": "i"}})
            elif op == "starts_with":
                match_conditions.append({col: {"$regex": f"^{re.escape(str(val))}", "$options": "i"}})
            elif op == "ends_with":
                match_conditions.append({col: {"$regex": f"{re.escape(str(val))}$", "$options": "i"}})

        if not match_conditions:
            return None

        if len(match_conditions) == 1:
            return match_conditions[0]

        if logic == "or":
            return {"$or": match_conditions}
        else:
            return {"$and": match_conditions}

    def _build_sort_stage(self, step: Dict[str, Any]) -> Optional[Dict]:
        """Build $sort stage from sort step."""
        columns = step.get("columns", [])

        if not columns:
            return None

        sort_spec = {}
        for sort_col in columns:
            col = sort_col.get("column", "")
            if not col:
                continue
            direction = sort_col.get("direction", "asc").lower()
            sort_spec[col] = 1 if direction == "asc" else -1

        return sort_spec if sort_spec else None

    def _build_lookup_stage(self, step: Dict[str, Any]) -> Optional[Dict]:
        """Build $lookup stage from join step."""
        join_collection = step.get("table")
        on_conditions = step.get("on", [])

        if not join_collection or not on_conditions:
            return None

        # MongoDB $lookup supports simple equality joins
        # For the first condition, use localField/foreignField
        first_cond = on_conditions[0]
        local_field = first_cond.get("left", "")
        foreign_field = first_cond.get("right", "")

        if not local_field or not foreign_field:
            return None

        lookup = {
            "$lookup": {
                "from": join_collection,
                "localField": local_field,
                "foreignField": foreign_field,
                "as": f"joined_{join_collection}"
            }
        }

        return lookup

    def _build_group_stage(self, step: Dict[str, Any]) -> Optional[Dict]:
        """Build $group stage from group_by step."""
        group_cols = step.get("columns", [])
        aggregations = step.get("aggregations", [])

        if not group_cols and not aggregations:
            return None

        # Build _id for grouping
        if len(group_cols) == 1:
            group_id = f"${group_cols[0]}"
        elif len(group_cols) > 1:
            group_id = {col: f"${col}" for col in group_cols}
        else:
            group_id = None  # Group all documents

        group_stage = {"_id": group_id}

        # Add group columns to output (for multi-column grouping)
        for col in group_cols:
            group_stage[col] = {"$first": f"${col}"}

        # Build aggregations
        for agg in aggregations:
            col = agg.get("column")
            func = agg.get("function", "sum").upper()
            alias = agg.get("alias", f"{func.lower()}_{col}" if col else func.lower())

            if func == "COUNT" and (col == "*" or not col):
                group_stage[alias] = {"$sum": 1}
            elif func == "COUNT":
                group_stage[alias] = {"$sum": {"$cond": [{"$ne": [f"${col}", None]}, 1, 0]}}
            elif func == "COUNT_DISTINCT":
                group_stage[alias] = {"$addToSet": f"${col}"}
            elif func == "SUM":
                group_stage[alias] = {"$sum": f"${col}"}
            elif func == "AVG":
                group_stage[alias] = {"$avg": f"${col}"}
            elif func == "MIN":
                group_stage[alias] = {"$min": f"${col}"}
            elif func == "MAX":
                group_stage[alias] = {"$max": f"${col}"}
            elif func == "FIRST":
                group_stage[alias] = {"$first": f"${col}"}
            elif func == "LAST":
                group_stage[alias] = {"$last": f"${col}"}

        return group_stage

    def _build_deduplicate_stage(
        self,
        step: Dict[str, Any],
        available_columns: Optional[List[str]]
    ) -> List[Dict]:
        """Build deduplication stages (group + project)."""
        dedup_cols = step.get("columns", [])

        if not dedup_cols:
            return []

        # Use $group with $first to keep first occurrence
        if len(dedup_cols) == 1:
            group_id = f"${dedup_cols[0]}"
        else:
            group_id = {col: f"${col}" for col in dedup_cols}

        group_stage = {"_id": group_id}

        # Keep first value of each field
        if available_columns:
            for col in available_columns:
                if col not in dedup_cols:
                    group_stage[col] = {"$first": f"${col}"}

        # Also include dedup columns
        for col in dedup_cols:
            group_stage[col] = {"$first": f"${col}"}

        return [{"$group": group_stage}]

    def _build_project_stage(
        self,
        selected_columns: Optional[List[str]],
        renames: Dict[str, str],
        dropped: set,
        available_columns: Optional[List[str]]
    ) -> Optional[Dict]:
        """Build $project stage for select, rename, drop operations."""
        project = {}

        # Handle explicit column selection
        if selected_columns:
            for col in selected_columns:
                if col in dropped:
                    continue
                new_name = renames.get(col, col)
                if new_name != col:
                    project[new_name] = f"${col}"
                else:
                    project[col] = 1

            # Exclude _id if not selected
            if "_id" not in selected_columns:
                project["_id"] = 0

        # Handle renames without explicit select
        elif renames:
            for old_name, new_name in renames.items():
                project[new_name] = f"${old_name}"
                if old_name not in project:
                    project[old_name] = 0  # Exclude old name

        # Handle dropped columns
        if dropped and not selected_columns:
            for col in dropped:
                project[col] = 0

        return project if project else None

    def _build_cast_expression(self, col: str, to_type: str) -> Dict:
        """Build cast expression for a column."""
        type_map = {
            "string": "$toString",
            "text": "$toString",
            "int": "$toInt",
            "integer": "$toInt",
            "long": "$toLong",
            "bigint": "$toLong",
            "double": "$toDouble",
            "decimal": "$toDouble",
            "float": "$toDouble",
            "bool": "$toBool",
            "boolean": "$toBool",
            "date": "$toDate",
            "objectid": "$toObjectId",
        }

        mongo_type = type_map.get(to_type.lower(), "$toString")
        return {mongo_type: f"${col}"}

    def _parse_expression(self, expression: str) -> Any:
        """
        Parse a simple expression string into MongoDB format.

        Supports:
        - Field references: field_name or $field_name
        - Simple arithmetic: field1 + field2, field * 2
        - String literals: 'value' or "value"
        - Numbers: 123, 45.67
        """
        expression = expression.strip()

        # Check for simple field reference
        if expression.startswith("$"):
            return expression

        # Check for quoted string
        if (expression.startswith("'") and expression.endswith("'")) or \
           (expression.startswith('"') and expression.endswith('"')):
            return expression[1:-1]

        # Check for number
        try:
            if "." in expression:
                return float(expression)
            return int(expression)
        except ValueError:
            pass

        # Check for arithmetic operations
        for op, mongo_op in [("+", "$add"), ("-", "$subtract"), ("*", "$multiply"), ("/", "$divide")]:
            if op in expression:
                parts = expression.split(op, 1)
                if len(parts) == 2:
                    left = self._parse_expression(parts[0])
                    right = self._parse_expression(parts[1])
                    # Convert field names to $ references
                    if isinstance(left, str) and not left.startswith("$"):
                        left = f"${left}"
                    if isinstance(right, str) and not right.startswith("$"):
                        right = f"${right}"
                    return {mongo_op: [left, right]}

        # Assume it's a field reference
        return f"${expression}"

    def _like_to_regex(self, like_pattern: str) -> str:
        """Convert SQL LIKE pattern to regex."""
        if not like_pattern:
            return ".*"

        # Escape regex special chars except % and _
        pattern = re.escape(like_pattern)
        # Convert SQL wildcards to regex
        pattern = pattern.replace(r"\%", ".*")
        pattern = pattern.replace(r"\_", ".")

        return f"^{pattern}$"


# Singleton instance
mongodb_transform_service = MongoDBTransformService()
