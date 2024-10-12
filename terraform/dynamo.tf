resource "aws_dynamodb_table" "log_table" {
  name         = var.project
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "log_identifier"
  range_key    = "timestamp"

  # Define attributes used in the table and GSIs
  attribute {
    name = "log_identifier"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  attribute {
    name = "is_high_outlier"
    type = "N"  # You could use N (1 or 0 for boolean-like values)
  }

  attribute {
    name = "is_low_outlier"
    type = "N"  # You could use N (1 or 0 for boolean-like values)
  }

  # GSI for querying logs based on the high outlier flag
  global_secondary_index {
    name            = "is_high_outlier_index"
    hash_key        = "is_high_outlier"
    projection_type = "ALL"
  }

  # GSI for querying logs based on the low outlier flag
  global_secondary_index {
    name            = "is_low_outlier_index"
    hash_key        = "is_low_outlier"
    projection_type = "ALL"
  }

  # Example GSI to query by log_identifier
  global_secondary_index {
    name            = "log_identifier_index"
    hash_key        = "log_identifier"
    projection_type = "ALL"
  }

  # TTL configuration for automatic deletion of items
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
}
