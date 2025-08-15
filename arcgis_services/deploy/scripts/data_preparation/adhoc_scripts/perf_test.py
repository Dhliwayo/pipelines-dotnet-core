
    # Imports

print("Starting")
print("Importing dependencies")

import arcpy
import os
from arcpy import env
from time import perf_counter
import requests    
from helpers import get_logger
import csv

logger = get_logger("perf_test.py", "./perf_test.log")

constraining_fc = r"\\lwukwvri53\d$\esriuk\FGDB\PERILS_B.gdb\UK_COUNTRY"
output_path=r"\\lwukwvri53\d$\PnPRasterPerfomanceTest\data\perf_tests.gdb"


def create_testing_points():
    logger.info("Creating points....")
    logger.info(arcpy.GetMessages())
    arcpy.management.CreateRandomPoints(output_path,"random_points_v1",constraining_fc,None,500,None,None,None)
    arcpy.management.CreateRandomPoints(output_path,"random_points_v2",constraining_fc,None,2000,None,None,None)
    logger.info(arcpy.GetMessages())
    logger.info("Done creating points....")

def run_tests():
    output_csv_file_test_1=r"\\lwukwvri53\d$\PnPRasterPerfomanceTest\data\perf_test_run_1.csv"
    input_points_test_1 = output_path+"\\"+"random_points"
    run_test_case(output_csv_file_test_1, input_points_test_1)

    output_csv_file_test_2=r"\\lwukwvri53\d$\PnPRasterPerfomanceTest\data\perf_test_run_2.csv"
    input_points_test_2 = output_path+"\\"+"random_points_v2"
    run_test_case(output_csv_file_test_2, input_points_test_2)


def run_test_case(output_csv_file, input_points):
    try:
        if os.path.exists(output_csv_file):
            os.remove(output_csv_file)

        header = ['OID','xy', 'low_res_rmt_gbp_time', 'low_res_rmt_tiff_time', 'high_res_ukf_gpb_time','high_res_ukf_tiff_time','low_res_rmt_gbp_result', 'low_res_rmt_tiff_result', 'high_res_ukf_gpb_result','high_res_ukf_tiff_result']
        with open(output_csv_file, 'x') as f:
            writer = csv.writer(f)
            writer.writerow(header)

            with arcpy.da.SearchCursor(input_points,["SHAPE@XY","OID@"],None,None,4326,None,None,None,None,None) as cursor:
                for row in cursor:
                    logger.info(f"Processing point....{row}")
                    x = row[0][0]
                    y = row[0][1]
                    oid=row[1]
                    low_res_uk_remoteness_gdb_url = f"https://lwukwvri53.opd.ads.uk.rsa-ins.com/GeoAssessment/GeoAssessment.svc/json/CalculatePerils?X={x}&Y={y}&Models=uk_remoteness_gdb"
                    low_res_uk_remoteness_tif_url = f"https://lwukwvri53.opd.ads.uk.rsa-ins.com/GeoAssessment/GeoAssessment.svc/json/CalculatePerils?X={x}&Y={y}&Models=uk_remoteness_tif"
                    high_res_uk_flood_sw_cl_gdb_url = f"https://lwukwvri53.opd.ads.uk.rsa-ins.com/GeoAssessment/GeoAssessment.svc/json/CalculatePerils?X={x}&Y={y}&Models=UK_FLOOD_SW_CL_gbb"
                    high_res_uk_flood_sw_cl_tiff_url = f"https://lwukwvri53.opd.ads.uk.rsa-ins.com/GeoAssessment/GeoAssessment.svc/json/CalculatePerils?X={x}&Y={y}&Models=UK_FLOOD_SW_CL_tif"

                    high_res_uk_flood_sw_cl_tiff_url_result =time_url_request(high_res_uk_flood_sw_cl_tiff_url)
                    low_res_uk_remoteness_gdb_url_result = time_url_request(low_res_uk_remoteness_gdb_url)
                    low_res_uk_remoteness_tif_url_result =time_url_request(low_res_uk_remoteness_tif_url)
                    high_res_uk_flood_sw_cl_gdb_url_result =time_url_request(high_res_uk_flood_sw_cl_gdb_url)


                    output = [oid,row[0], 
                            low_res_uk_remoteness_gdb_url_result['request_time_sec'],
                            low_res_uk_remoteness_tif_url_result['request_time_sec'], 
                            high_res_uk_flood_sw_cl_gdb_url_result['request_time_sec'],
                            high_res_uk_flood_sw_cl_tiff_url_result['request_time_sec'],
                            low_res_uk_remoteness_gdb_url_result['response'], 
                            low_res_uk_remoteness_tif_url_result['response'], 
                            high_res_uk_flood_sw_cl_gdb_url_result['response'],
                            high_res_uk_flood_sw_cl_tiff_url_result['response']]
                    
                    writer.writerow(output)

        logger.info(f"Done running tests....")
    except Exception as e:
        logger.info(arcpy.GetMessages())
        logger.error(e)
        

def time_url_request(serviceURL):
    try:
        start = perf_counter()
        response = requests.get(url=serviceURL,verify=False)
        end = perf_counter()

        request_time_sec = end - start
        return {"url":serviceURL, "response":response.content, "request_time_sec":request_time_sec}
    except Exception as e:
        logger.info(arcpy.GetMessages())
        logger.error(e)

if __name__ == "__main__":
    #create_testing_points()
    run_tests()