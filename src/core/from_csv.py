# import csv
# from schemas import UserFromCsv
#
# def create_full_name(user: UserFromCsv):
#     return str(user.last_name) + " " + str(user.first_name) + " " + str(user.fatherland)
#
#
# def read_from_csv(csv_name):
#     with open(csv_name, encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile, delimiter='\t', skipinitialspace=False)
#         list_result_parse = list()
#         for row in reader:
#             list_result_parse.append(UserFromCsv.parse_obj(row))
#     return list_result_parse