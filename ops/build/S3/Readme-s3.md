# S3 bucket creating and configuration
### We are using s3 buckects to store the manifest, video,audio fragments, our videos sources,smil configuaration files and the ouput of the hacking simulation from our python scripts. We are using it integrated with cloudfront CDN to delivery stealed stream signal we are simulating. The cloudfront configuartion is apart.

1. In the left navigation pane, choose **Buckets**.
2. Choose **Create bucket**.   
        
   ![S3 buckect](/ops/img/s3.jpg) 

3. For **Bucket name** enter `testbucket-watermarking`
4. For **Region** use `us-east-1`
5. Under Object **Ownership** choose `ACLs enabled`
6. For **Buckect policy** insert the content of `s3-permission.json` file  
7. For **Bucket Versioning** select `disable`
8. For **Default encryption** select `Server-side encryption with Amazon S3 managed keys (SSE-S3)`
9. Finally select **Create bucket**
