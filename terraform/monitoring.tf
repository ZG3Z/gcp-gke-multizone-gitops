resource "google_monitoring_dashboard" "main" {
  dashboard_json = jsonencode({
    displayName = "FastAPI GKE Dashboard"

    mosaicLayout = {
      columns = 12

      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "Pod CPU Usage"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"k8s_container\" resource.labels.cluster_name=\"${var.cluster_name}\" resource.labels.namespace_name=\"default\" resource.labels.container_name=\"fastapi\" metric.type=\"kubernetes.io/container/cpu/core_usage_time\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_MEAN"
                      groupByFields      = ["resource.pod_name"]
                    }
                  }
                }
                plotType = "LINE"
              }]
              yAxis = {
                label = "CPU Cores"
                scale = "LINEAR"
              }
            }
          }
        },

        {
          xPos   = 6
          width  = 6
          height = 4
          widget = {
            title = "Pod Memory Usage (MB)"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"k8s_container\" resource.labels.cluster_name=\"${var.cluster_name}\" resource.labels.namespace_name=\"default\" resource.labels.container_name=\"fastapi\" metric.type=\"kubernetes.io/container/memory/used_bytes\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_MEAN"
                      crossSeriesReducer = "REDUCE_MEAN"
                      groupByFields      = ["resource.pod_name"]
                    }
                  }
                }
                plotType = "LINE"
              }]
              yAxis = {
                label = "Memory (Bytes)"
                scale = "LINEAR"
              }
            }
          }
        },

        {
          yPos   = 4
          width  = 6
          height = 3
          widget = {
            title = "Running Pods"
            scorecard = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"k8s_pod\" resource.labels.cluster_name=\"${var.cluster_name}\" resource.labels.namespace_name=\"default\" metric.type=\"kubernetes.io/pod/network/received_bytes_count\""
                  aggregation = {
                    alignmentPeriod    = "60s"
                    perSeriesAligner   = "ALIGN_RATE"
                    crossSeriesReducer = "REDUCE_COUNT"
                  }
                }
              }
              sparkChartView = {
                sparkChartType = "SPARK_LINE"
              }
            }
          }
        },

        {
          yPos   = 4
          xPos   = 6
          width  = 6
          height = 3
          widget = {
            title = "Network Received (Bytes/sec)"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"k8s_pod\" resource.labels.cluster_name=\"${var.cluster_name}\" resource.labels.namespace_name=\"default\" metric.type=\"kubernetes.io/pod/network/received_bytes_count\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                    }
                  }
                }
                plotType = "LINE"
              }]
              yAxis = {
                label = "Bytes/sec"
                scale = "LINEAR"
              }
            }
          }
        }
      ]
    }
  })
}