variable "tags" {
    description = "Name of the environment"
    default = "stage"
}

variable "stream_name" {
    description = "Name of the stream to be created"
}

variable "shard_count" {
    type = number
    default = 2
}

variable "retention_period" {
    type = number
    default = 48
}

variable "shard_level_metrics" {
    type = list(string)
    default = [  
        "IncomingBytes",
        "OutgoingBytes",
        "IncomingRecords",
        "OutgoingRecords",
        "ReadProvisionedThroughputExceeded",
        "WriteProvisionedThroughputExceeded"]
}