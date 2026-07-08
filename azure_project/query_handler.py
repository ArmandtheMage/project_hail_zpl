

class  QueryMaker:
    """Builder for Azure DevOps WIQL (Work Item Query Language) queries.

    Constructs SELECT statements with configurable fields and WHERE constraints,
    targeting a specific Azure DevOps project.

    Args:
        connection: Azure DevOps Connection object (used for future extensions).
        fields_to_take: List of field names to include in the SELECT clause.
            Defaults to common fields (Id, WorkItemType, Title, AssignedTo, State, Tags).
        constraints: List of QueryConstraints to apply in the WHERE clause.
    """

    def __init__(self, connection, fields_to_take=[], constraints=[]):
        self.connection = connection
        self.fields_to_take = self.get_fields_to_take(fields_to_take)
        self._constraints = constraints

    def get_fields_to_take(self, fields_to_take):
        """Convert a list of field names to Azure DevOps format ([System.Field]).

        If no fields are provided, returns a default set of common work item fields.

        Args:
            fields_to_take: List of short field names (e.g. "Title", "State").

        Returns:
            List of fields formatted as Azure DevOps references (e.g. "[System.Title]").
        """
        if not fields_to_take:
            fields_to_take = ["Id", "WorkItemType", "Title", "AssignedTo", "State", "Tags"] # Found in build & Product Version

        return [self.get_field_as_azure_field(field) for field in fields_to_take]

    @property
    def constraints(self):
        return self._constraints

    @constraints.setter
    def constraints(self, value):
        if isinstance(value, list):
            self._constraints.extend(value)
        else:
            self._constraints.append(value)

    def add_field_to_take(self, field, isCustomField=False):
        """Add a field to the SELECT clause.

        Args:
            field: Short field name (e.g. "Priority").
            isCustomField: If True, prefixes with 'Custom.' instead of 'System.'.
        """
        azure_field = self.get_field_as_azure_field(field, isCustomField)
        self.fields_to_take.append(azure_field)

    @classmethod
    def get_field_as_azure_field(cls, field, isCustomField=False):
        """Format a field name into Azure DevOps WIQL reference notation.

        Args:
            field: Short field name (e.g. "Title", "ProductVersion").
            isCustomField: If True, returns "[Custom.<field>]"; otherwise "[System.<field>]".

        Returns:
            Formatted field string ready for WIQL queries.
        """
        if isCustomField:
            return f"[Custom.{field}]"
        return f"[System.{field}]"

    def build_query(self, project_name):
        """Build the complete WIQL query string.

        Assembles SELECT fields, FROM workitems, and WHERE clauses including
        the project filter and all registered constraints.

        Args:
            project_name: The Azure DevOps project name to filter on.

        Returns:
            A complete WIQL query string ready to be executed.
        """
        query = "SELECT "
        query += ", ".join([f"{field}" for field in self.fields_to_take])
        query += " FROM workitems WHERE "
        query += f"[System.TeamProject] = '{project_name} '"
        query += " ".join([f"{constraint.logic_operator} {constraint.field} {constraint.operator} '{constraint.value}'" for constraint in self.constraints])
        return query

class QueryConstraints:
    """Represents a single WHERE clause constraint for a WIQL query.

    Each constraint consists of a field, a comparison operator, a value,
    and a logical operator (AND/OR) to chain with other constraints.

    Args:
        field: Short field name (e.g. "State", "ProductVersion").
        operator: Comparison operator (=, <>, CONTAINS, etc.).
        value: The value to compare the field against.
        logic_operator: Logical operator to prepend (AND/OR). Defaults to AND.
        isCustomField: If True, treats the field as a Custom field.
    """

    LOGIC_OPERATORS = ["AND", "OR"]
    COMPARISON_OPERATORS = ["=", "<>", ">", "<", ">=", "<=", "CONTAINS", "DOES NOT CONTAIN", "IN", "NOT IN"]
    
    def __init__(self, field, operator, value, logic_operator=None, isCustomField=False):
        self.field = QueryMaker.get_field_as_azure_field(field, isCustomField)
        self.operator = operator if operator in self.COMPARISON_OPERATORS else '<>'
        self.value = value
        self.logic_operator = logic_operator if logic_operator in self.LOGIC_OPERATORS else 'AND'

    def get_constraint_as_tuple(self):
        """Return the constraint as a tuple (logic_operator, field, operator, value)."""
        return (self.logic_operator, self.field, self.operator, self.value)

    @classmethod
    def create_constraint_as_tuple(cls, field, operator, value, logic_operator=None, isCustomField=False):
        """Factory method that creates a constraint and immediately returns it as a tuple.

        Args:
            field: Short field name.
            operator: Comparison operator.
            value: Value to compare against.
            logic_operator: AND/OR (defaults to AND).
            isCustomField: Whether the field uses the Custom. prefix.

        Returns:
            Tuple of (logic_operator, field, operator, value).
        """
        return cls(field, operator, value, logic_operator, isCustomField).get_constraint_as_tuple()
    
if __name__ == "__main__":
    connection = None  # Replace with your actual connection object
    constraints = [
        QueryConstraints.create_constraint_as_tuple("WorkItemType", "<>", "", "OR"),
        QueryConstraints.create_constraint_as_tuple("ProductVersion", "CONTAINS", "6.11", isCustomField=True),
        QueryConstraints.create_constraint_as_tuple("AreaPath", "=", "JOINON EVO - RaaS and APP\\MRE\\APP Team")
    ]
    

    query_maker = QueryMaker(connection, constraints=constraints)
    project_name = "JOINON EVO - RaaS and APP"
    query = query_maker.build_query(project_name)
    print(query)