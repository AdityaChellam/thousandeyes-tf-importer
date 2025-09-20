def import_block(resource_full_type: str, tf_name: str, external_id: str) -> str:
    return f"""import {{
  to = {resource_full_type}.{tf_name}
  id = "{external_id}"
}}"""
