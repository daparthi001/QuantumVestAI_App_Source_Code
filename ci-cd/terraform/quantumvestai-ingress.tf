resource "kubernetes_ingress_v1" "quantumvestai" {
  metadata {
    name = "quantumvestai-ingress"
    annotations = {
      "kubernetes.io/ingress.class"                   = "alb"
      "alb.ingress.kubernetes.io/scheme"              = "internet-facing"
      "alb.ingress.kubernetes.io/listen-ports"        = "[{\"HTTP\": 80}, {\"HTTPS\": 443}]"
      "alb.ingress.kubernetes.io/certificate-arn"     = "arn:aws:acm:us-east-1:YOUR_ACCOUNT_ID:certificate/YOUR_CERT_ID"
      "alb.ingress.kubernetes.io/ssl-redirect"        = "443"
      "alb.ingress.kubernetes.io/target-type"         = "ip"
    }
  }

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
