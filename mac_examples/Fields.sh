python ..//jsonpush.py --createfields "fields.json" -org "organizationId" -source "SourceId" -apikey "ApiKey" -json "./Products/test.json" -uri "https://www.test.com/catalog/%%[product_id]" --action "UPDATE" --key "%%[product_id]-%%[product_details]-p" --quickview "my.HTML"