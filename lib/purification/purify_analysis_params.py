"""
Contains analysis parameters for purification measurements. Such as temporal filters
"""

filter_settings = {
	
	'st_start' 		: 2772.5e3,#4.5e3,
	'st_len'		: 40e3,
	'st_len_w2' 	: 40e3,
	'min_cr_lt3_before'	: 1,
	'min_cr_lt4_before'	: 1,
	'min_cr_lt3_after'	: 1,
	'min_cr_lt4_after'	: 1,
	'max_reps_w1'	: 1000,
	'min_reps_w1'	: 1,
	'max_reps_w2'	: 50,
	'min_reps_w2'	: 1,
	'max_dt'		: 40e3,
}

data_settings = {

	'base_folder_lt3' : r'D:\measuring\data\Purification_lt3_raw_data',
	'base_folder_lt4' : r'D:\measuring\data\Purification_lt4_raw_data',
	'shifted_data_correction_time'	: 2772.5e3-2791.5e3,
	'shifted_data_start_offset_ch1' : 1.8e3,
	'unshifted_days'				: ['20160714','20160715','20160716','20160718','20160719','20160720','20160721','20160722','20160724','20160725','20160726','20160727',\
									   '20160807','20160808'],
	'shifted_days'					: ['20160811','20160816','20160818','20160819','20160820','20160821','20160822','20160823','20160824'],
	'theta_folders'					: {'pi/4': r'\Purify_XX_First_Attempts', 'pi/5': r'\Purify_35percent_theta', 'pi/6': r'\Purify_25percent_theta', 'pi/8': r'\Purify_15percent_theta'},

	'ssro_calib_lt3' : '20160716_'+'091002',
	'ssro_calib_lt4' : '20160716_'+'113952',

}