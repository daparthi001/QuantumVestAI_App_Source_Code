  spec {
    rule {
      host = "quantumvestai.com"
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = "ai-stock-agent-service"
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}
