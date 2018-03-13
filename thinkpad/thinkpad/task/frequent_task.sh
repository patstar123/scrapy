LOG_NAME=frequent.log

export PATH=$PATH:/usr/local/bin/

echo "" >> ${LOG_NAME}
echo "" >> ${LOG_NAME}
echo "========================================" >> ${LOG_NAME}
echo `date` >> ${LOG_NAME}
echo "========================================" >> ${LOG_NAME}
echo "-----------outlet_specified" >> ${LOG_NAME}
rm -f outlet_specified.csv >> ${LOG_NAME} 2>&1
scrapy crawl outlet_specified -o outlet_specified.csv -L WARNING >> ${LOG_NAME} 2>&1
mv outlet_specified.csv last_outlet_specified.csv
