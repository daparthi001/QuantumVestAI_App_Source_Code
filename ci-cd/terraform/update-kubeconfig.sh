#!/bin/bash
aws eks update-kubeconfig --region us-east-1 --name quantumvestai-cluster
echo "Kubeconfig updated for cluster quantumvestai-cluster"
