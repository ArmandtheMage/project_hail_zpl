

class  QueryMaker:
    def __init__(self, connection, fields_to_take=[], constraints:list[QueryConstraints]=[]):
        self.connection = connection
        self.fields_to_take = self.get_fields_to_take(fields_to_take)
        self._constraints = constraints

    def get_fields_to_take(self, fields_to_take):
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
        azure_field = self.get_field_as_azure_field(field, isCustomField)
        self.fields_to_take.append(azure_field)

    @classmethod
    def get_field_as_azure_field(cls, field, isCustomField=False):
        if isCustomField:
            return f"[Custom.{field}]"
        return f"[System.{field}]"

    def build_query(self, project_name):
        query = "SELECT "
        query += ", ".join([f"{field}" for field in self.fields_to_take])
        query += " FROM workitems WHERE "
        query += f"[System.TeamProject] = '{project_name} '"
        query += " ".join([f"{constraint.logic_operator} {constraint.field} {constraint.operator} '{constraint.value}'" for constraint in self.constraints])
        return query
    
class QueryConstraints:
    LOGIC_OPERATORS = ["AND", "OR"]
    COMPARISON_OPERATORS = ["=", "<>", ">", "<", ">=", "<=", "CONTAINS", "DOES NOT CONTAIN", "IN", "NOT IN"]
    
    def __init__(self, field, operator, value, logic_operator=None, isCustomField=False):
        self.field = QueryMaker.get_field_as_azure_field(field, isCustomField)
        self.operator = operator if operator in self.COMPARISON_OPERATORS else '<>'
        self.value = value
        self.logic_operator = logic_operator if logic_operator in self.LOGIC_OPERATORS else 'AND'

    def get_constraint_as_tuple(self):
        return (self.logic_operator, self.field, self.operator, self.value)

    @classmethod
    def create_constraint_as_tuple(cls, field, operator, value, logic_operator=None, isCustomField=False):
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