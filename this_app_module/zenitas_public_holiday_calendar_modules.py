# from datetime import date as dt
# from datetime import timedelta as td
# import holidays
# import calendar

# def _get_base_calendar() -> str:
#     result_fields = [
#         'calendar_date',
#         'calendar_date_identifier',
#         'year_day',
#         'quarter_day',
#         'month_day',
#         'claro_fortnight_day',
#         'plena_fortnight_day',
#         'iso8601_weekday',
#         'weekday_name',
#         'weekday_name_short',
#         'calendar_year',
#         'year_identifier',
#         'year_starting',
#         'year_ending',
#         'year_is_leap',
#         'year_num_of_days',
#         'fiscal_year',
#         'fiscal_year_identifier',
#         'fiscal_year_starting',
#         'fiscal_year_ending',
#         'fiscal_year_num_of_days',
#         'calendar_quarter',
#         'quarter_identifier',
#         'quarter_starting',
#         'quarter_ending',
#         'quarter_num_of_days',
#         'calendar_month',
#         'month_identifier',
#         'month_name',
#         'month_name_short',
#         'month_starting',
#         'month_ending',
#         'month_num_of_days',
#         'claro_fortnight_identifier',
#         'claro_fortnight_starting',
#         'claro_fortnight_ending',
#         'plena_fortnight_identifier',
#         'plena_fortnight_starting',
#         'plena_fortnight_ending',
#         'iso8601_week_year',
#         'iso8601_week',
#         'iso8601_week_identifier',
#         'week_starting',
#         'week_ending'
#     ]
#     result_string = ','.join(result_fields)
#     claro_fortnight_starting_base_date = dt(2000, 1, 10)
#     plena_fortnight_starting_base_date = dt(2000, 1, 3)
#     for year in range(dt.today().year - 10, dt.today().year + 10):
#         for month in range(1, 13):
#             for day in range(1, calendar.monthrange(year, month)[1] + 1):
#                 current_date = dt(year, month, day)
#                 date_iso_identifier = current_date.isoformat()
#                 year = current_date.year
#                 month = current_date.month
#                 quarter = (month - 1) // 3 + 1
#                 iso_week = current_date.isocalendar()[1]
#                 iso_week_year = current_date.isocalendar()[0]
#                 iso_weekday = current_date.isoweekday()

#                 year_identifier = f'CY{year:04d}'
#                 year_starting = dt(year, 1, 1)
#                 year_ending = dt(year, 12, 31)
#                 year_is_leap = calendar.isleap(year)
#                 year_num_of_days = (year_ending - year_starting).days + 1

#                 fiscal_year = year if month >= 7 else year - 1
#                 fiscal_year_identifier = f'FY{year:04d}-{year + 1:04d}' if month >= 7 else f'FY{year - 1:04d}-{year:04d}'
#                 fiscal_year_starting = dt(fiscal_year, 7, 1)
#                 fiscal_year_ending = dt(fiscal_year + 1, 6, 30)
#                 fiscal_year_num_of_days = (fiscal_year_ending - fiscal_year_starting).days + 1

#                 quarter_identifier = f'{year_identifier}Q{quarter}'
#                 quarter_starting = dt(year, (quarter - 1) * 3 + 1, 1)
#                 quarter_ending = dt(year, quarter * 3, calendar.monthrange(year, quarter * 3)[1])
#                 quarter_num_of_days = (quarter_ending - quarter_starting).days + 1

#                 month_identifier = f'{year_identifier}M{month:02d}'
#                 month_name = calendar.month_name[month]
#                 month_name_short = calendar.month_abbr[month]
#                 month_starting = dt(year, month, 1)
#                 month_ending = dt(year, month, calendar.monthrange(year, month)[1])
#                 month_num_of_days = (month_ending - month_starting).days + 1

#                 claro_fortnight_starting = claro_fortnight_starting_base_date + td(days = (current_date - claro_fortnight_starting_base_date).days // 14 * 14)
#                 claro_fortnight_ending = claro_fortnight_starting + td(days = 13)
#                 claro_fortnight_identifier = f'claro_fn_{claro_fortnight_starting.isoformat()}_to_{claro_fortnight_ending.isoformat()}'
                
#                 plena_fortnight_starting = plena_fortnight_starting_base_date + td(days = (current_date - plena_fortnight_starting_base_date).days // 14 * 14)
#                 plena_fortnight_ending = plena_fortnight_starting + td(days = 13)
#                 plena_fortnight_identifier = f'plena_fn_{plena_fortnight_starting.isoformat()}_to_{plena_fortnight_ending.isoformat()}'
                
#                 iso_week_identifier = f'ISO8601_Y{iso_week_year:04d}W{iso_week:02d}' 
#                 iso_week_starting = current_date - td(days = dt.weekday(current_date))
#                 iso_week_ending = current_date + td(days = (6 - dt.weekday(current_date)))

#                 day_of_year = current_date.timetuple().tm_yday
#                 day_of_quarter = (current_date - quarter_starting).days + 1
#                 day_of_month = day
#                 day_of_week = iso_weekday
#                 day_of_claro_fortnight = (current_date - claro_fortnight_starting).days + 1
#                 day_of_plena_fortnight = (current_date - plena_fortnight_starting).days + 1
#                 weekday_name = calendar.day_name[iso_weekday - 1]
#                 weekday_name_short = calendar.day_abbr[iso_weekday - 1]

#                 this_line = [
#                     f'{current_date}',
#                     f'{date_iso_identifier}',
#                     f'{day_of_year}',
#                     f'{day_of_quarter}',
#                     f'{day_of_month}',
#                     f'{day_of_claro_fortnight}',
#                     f'{day_of_plena_fortnight}',
#                     f'{iso_weekday}',
#                     f'{weekday_name}',
#                     f'{weekday_name_short}',
#                     f'{year}',
#                     f'{year_identifier}',
#                     f'{year_starting}',
#                     f'{year_ending}',
#                     f'{year_is_leap}',
#                     f'{year_num_of_days}',
#                     f'{fiscal_year}',
#                     f'{fiscal_year_identifier}',
#                     f'{fiscal_year_starting}',
#                     f'{fiscal_year_ending}',
#                     f'{fiscal_year_num_of_days}',
#                     f'{quarter}',
#                     f'{quarter_identifier}',
#                     f'{quarter_starting}',
#                     f'{quarter_ending}',
#                     f'{quarter_num_of_days}',
#                     f'{month}',
#                     f'{month_identifier}',
#                     f'{month_name}',
#                     f'{month_name_short}',
#                     f'{month_starting}',
#                     f'{month_ending}',
#                     f'{month_num_of_days}',
#                     f'{claro_fortnight_identifier}',
#                     f'{claro_fortnight_starting}',
#                     f'{claro_fortnight_ending}',
#                     f'{plena_fortnight_identifier}',
#                     f'{plena_fortnight_starting}',
#                     f'{plena_fortnight_ending}',
#                     f'{iso_week_year}',
#                     f'{iso_week}',
#                     f'{iso_week_identifier}',
#                     f'{iso_week_starting}',
#                     f'{iso_week_ending}'
#                 ]
#                 # append to result_dstring as a new line
#                 result_string += f'\n{",".join(this_line)}'
#     return result_string

# def _get_holiday_calendar() -> str:
#     result_string = 'state,date,holiday_name'
#     for sub_d in [None, 'VIC', 'NSW', 'QLD', 'SA', 'WA', 'TAS', 'ACT', 'NT']:
#         au_holidays = holidays.Australia(subdiv=sub_d, years=range(dt.today().year - 3, dt.today().year + 3))
#         for date, name in sorted(au_holidays.items()):
#             if sub_d is None:
#                 # append to result_string as a new line
#                 result_string += f'\nNATIONAL,{date},{name}'
#             else:    
#                 # append to result_string as a new line
#                 result_string += f'\n{sub_d},{date},{name}'
#     return result_string