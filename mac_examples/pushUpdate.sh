python ../jsonpush.py -org "organizationId" -source "SourceId" -apikey "ApiKey" -json "./Products/test.json" -uri "https://www.com.com/catalog/%%[product_details]-%%[product_id]-p" --action "UPDATE" --key "%%[product_id]-%%[product_details]-p" --quickview "my.HTML"
