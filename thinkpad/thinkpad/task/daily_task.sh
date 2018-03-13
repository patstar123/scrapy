LOG_NAME=daily.log

export PATH=$PATH:/usr/local/bin/

echo "" >> ${LOG_NAME}
echo "" >> ${LOG_NAME}
echo "========================================" >> ${LOG_NAME}
echo `date` >> ${LOG_NAME}
echo "========================================" >> ${LOG_NAME}
echo "-----------perksoffer_clearance_sale" >> ${LOG_NAME}
rm -f perksoffer_clearance_sale.csv >> ${LOG_NAME} 2>&1
scrapy crawl perksoffer_clearance_sale -o perksoffer_clearance_sale.csv -L WARNING >> ${LOG_NAME} 2>&1
mv perksoffer_clearance_sale.csv last_perksoffer_clearance_sale.csv

echo "-----------perksoffer_consumer_sale" >> ${LOG_NAME}
rm -f perksoffer_consumer_sale.csv >> ${LOG_NAME} 2>&1
scrapy crawl perksoffer_consumer_sale -o perksoffer_consumer_sale.csv -L WARNING >> ${LOG_NAME} 2>&1
mv perksoffer_consumer_sale.csv last_perksoffer_consumer_sale.csv

echo "-----------perksoffer_monthly_sale" >> ${LOG_NAME}
rm -f perksoffer_monthly_sale.csv >> ${LOG_NAME} 2>&1
scrapy crawl perksoffer_monthly_sale -o perksoffer_monthly_sale.csv -L WARNING >> ${LOG_NAME} 2>&1
mv perksoffer_monthly_sale.csv last_perksoffer_monthly_sale.csv

echo "-----------perksoffer_specified" >> ${LOG_NAME}
rm -f perksoffer_specified.csv >> ${LOG_NAME} 2>&1
scrapy crawl perksoffer_specified -o perksoffer_specified.csv -L WARNING >> ${LOG_NAME} 2>&1
mv perksoffer_specified.csv last_perksoffer_specified.csv

echo "-----------perksoffer_weekly_sale" >> ${LOG_NAME}
rm -f perksoffer_weekly_sale.csv >> ${LOG_NAME} 2>&1
scrapy crawl perksoffer_weekly_sale -o perksoffer_weekly_sale.csv -L WARNING >> ${LOG_NAME} 2>&1
mv perksoffer_weekly_sale.csv last_perksoffer_weekly_sale.csv
