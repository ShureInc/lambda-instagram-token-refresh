.PHONY: zip-lambda
zip-lambda:
	@echo --------- zip-lambda ---------
	@zip -r lambda.zip . -x "*.github/*" -x "*.git/*" -x ".gitignore" -x "Makefile" -x "Jenkinsfile"
	@echo "OK\n"

.PHONY: upload-zip-lambda
upload-zip-lambda:
	@echo --------- upload-zip-lambda ---------
	@aws s3 cp lambda.zip s3://use1-web-prod-gms-ppapp-instagram-lambda-s3/
	@echo "OK\n"	

.PHONY: deploy-lambda
deploy-lambda:
	@echo --------- deploy-lambda ---------
	@aws lambda update-function-code --function-name us-east-1-web-prod-gms-ppapp-instagram-token-rotate-lambda --s3-bucket use1-web-prod-gms-ppapp-instagram-lambda-s3 --s3-key lambda.zip
	@echo "OK\n"
	
.PHONY: ci
ci: zip-lambda upload-zip-lambda deploy-lambda