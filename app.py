from flask import Flask, render_template, redirect,  request, url_for, flash, session
import mysql.connector
from mysql.connector import Error
import random
import hashlib
from pyknow import *
import sys


class Patient(Fact):
	"""Info about the patient"""
	pass

age=""
agefact=""
o_psa=""
o_num_symp=""
output=""
pcd_treat=""
o_bph=""
o_pts=""

def SUMFIELDS(p, *fields):
	return sum([p.get(x, 0) for x in fields])

class InreferenceEngine(KnowledgeEngine):
	
	"""
	The age_risk_factors below are according to statistics from history of prostate cancer diagnostics and the value in the end is the percentange difference of risk eg. from age 20 upto 30 the percentage risk is from 2% to 8%, therefore, the age_risk_factor is 8%-2% = 6%
	"""
	global output, age, o_psa, o_num_symp, o_bph, o_pts, agefact
	#Age self declaration
	@Rule(Patient(Age=P(lambda x: x < 20)))
	def concerned_person(self):
		global age
		age = "Sorry, you're still young to take this test."
		

	#Age self declaration
	@Rule(Patient(Age=P(lambda x: x > 19)))
	def right_person(self):
		global age
		self.declare(Fact(pcpatient=True))
		age= "You're welcome patient."

	@Rule(Fact(pcpatient=True),
          Patient(Age=MATCH.Age))     
	def Age_Fact(self, Age):
		global agefact
		if Age in range(19, 31):
			self.declare(Fact(Age_factor=6))
			agefact="Age Factor is 6"
		elif Age in range(30, 41):
			self.declare(Fact(Age_factor=22))
			agefact="Age Factor is 22"
		elif Age in range(40, 61):
			self.declare(Fact(Age_factor=40))
			agefact="Age Factor is 40"
		elif Age in range(60, 71):
			self.declare(Fact(Age_factor=56))
			agefact="Age Factor is 56"
		elif Age in range(70, 81):
			self.declare(Fact(Age_factor=52))
			agefact="Age Factor is 52"
		elif Age in range(80, 91):
			self.declare(Fact(Age_factor=52))
			agefact="Age Factor is 52"
		else:
			agefact = "Invalid age for factoring or no known risk for factor for you age."

	#determine the risk depending on PSA levels(stable-rising).
	@Rule(Fact(pcpatient=True),Patient(psa=MATCH.psa))
	def psa_level(self, psa):
		global o_psa
		if psa == 'rising':
			self.declare(Fact(psa_risk=True))
			o_psa="Warning! You have high risk of having a prostate cancer tumor from your PSA level answer."
		elif psa == 'stable':
			self.declare(Fact(psa_risk=False))
			o_psa="You seem to have low risk of having a prostate cancer tumor from your PSA level answer, but you should take further tests, monthly"    
	
		
	"""
	below we are testing the number of symptoms a 
    patient can have which determinies the stage and 
    risk of prostate cancer deriving from the number of 
    symptoms and the age of the patient also.Prostage cancer stage risk is from low,
    meduium, high derived from the 12 common symptoms from the entry form.
	"""
	@Rule(Fact(pcpatient=True), AS.p << Patient(),
		TEST(lambda p: SUMFIELDS(p,
                                   'freq_night_urination',
                                   'bloody_semen',
                                   'painful_urination',
                                   'bloody_stool',
                                   'weak_urine_flow',
								   'painful_eju',
								   'inad_erec',
								   'erectile_dysfunc',
								   'pain_in_bones',
								   'swelling_lower_limbs') <= 4))
	def has_low_pc_risk(self, p):
		global o_num_symp
		self.declare(Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=True))
		o_num_symp="You have low risk of having a biopsy detectable prostate cancer cosidering your symptoms."

	
	@Rule(Fact(pcpatient=True),
	AS.p << Patient(),
	TEST(lambda p: SUMFIELDS(p,
                                   'freq_night_urination',
                                   'bloody_semen',
                                   'painful_urination',
                                   'bloody_stool',
                                   'weak_urine_flow',
								   'painful_eju',
								   'inad_erec',
								   'erectile_dysfunc',
								   'pain_in_bones',
								   'swelling_lower_limbs') > 4), 
         TEST(lambda p: SUMFIELDS(p,
                                   'freq_night_urination',
                                   'bloody_semen',
                                   'painful_urination',
                                   'bloody_stool',
                                   'weak_urine_flow',
								   'painful_eju',
								   'inad_erec',
								   'erectile_dysfunc',
								   'pain_in_bones',
								   'swelling_lower_limbs') < 9))
	def has_medium_pc_risk(self, p):
		global o_num_symp
		self.declare(Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=True))
		o_num_symp="You have medium risk of having a biopsy detectable pc since their attribute are that of prostate cancer"
	
	@Rule(Fact(pcpatient=True),
	AS.p << Patient(),
	TEST(lambda p: SUMFIELDS(p,
                                   'freq_night_urination',
                                   'bloody_semen',
                                   'painful_urination',
                                   'bloody_stool',
                                   'weak_urine_flow',
								   'painful_eju',
								   'inad_erec',
								   'erectile_dysfunc',
								   'pain_in_bones',
								   'swelling_lower_limbs') > 8), 
				TEST(lambda p: SUMFIELDS(p,
                                   'freq_night_urination',
                                   'bloody_semen',
                                   'painful_urination',
                                   'bloody_stool',
                                   'weak_urine_flow',
								   'painful_eju',
								   'inad_erec',
								   'erectile_dysfunc',
								   'pain_in_bones',
								   'swelling_lower_limbs') < 13))
	def has_high_pc_risk(self, p):
		global o_num_symp
		self.declare(Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=True))
		o_num_symp="You seem to have a high risk of having a biopsy detectable prostate cancer since their attribute are that of prostate cancer"

	"""
	WE are not determining the nature of the symptoms since there also other diseases with symptoms similar to those of prostate cancer
	"""
	@Rule(Fact(pcpatient=True),
	AS.p << Patient(),
	TEST(lambda p: SUMFIELDS(p,
                                   'freq_night_urination',
                                     'weak_urine_flow') == 2),
         TEST(lambda p: SUMFIELDS(p,
                                   'bloody_semen',
                                   'painful_urination',
                                   'bloody_stool',
								   'painful_eju',
								   'inad_erec',
								   'erectile_dysfunc',
								   'pain_in_bones',
								   'swelling_lower_limbs') == 0))
	def pcsymp_att(self):
		global o_bph
		self.declare(Fact(symp_prostate_cancer_att=False))
		o_bph="You seem to have symptoms similar to Benign Prostatic Hyperplasia. Your given symptoms are consistent with BPH. The symptoms of BPH include weak/slow urine stream, stoping and starting of urine and unempty bladder after urination."
	
	@Rule(Fact(pcpatient=True),
	AS.p << Patient(),
	TEST(lambda p: SUMFIELDS(p,
                                   'painful_urination',
                                   'weak_urine_flow',
								   'painful_eju',
								   'pain_in_bones') == 4),
         TEST(lambda p: SUMFIELDS(p,
                                   'freq_night_urination',
                                   'bloody_semen',
                                   'bloody_stool',
                                   'weak_urine_flow',
								   'inad_erec',
								   'erectile_dysfunc',
								   'swelling_lower_limbs') == 0))
	def pcsymp_att2(self):
		global o_pts
		self.declare(Fact(symp_prostate_cancer_att=False))
		o_pts="You seem to have symptoms similar to Prostatitis. The symptoms you have given are consistent of Prostatitis. The symptoms of Prostatitis include weak/slow urine stream, stoping and starting of urine and unempty bladder after urination. The symptoms also include high fever, strong urge to urinate but little urine."
		
	#if the given symtms do not match the given above the pc risk with given symp att if true
	
	"""
	Below we are finalising all the given answers from ten entry form and determing the prostate cancer type and the suggestions including taking further tests, possible medical treatments and any possibilities that the patient doesn't have prostate cancer but other diseases with similar symptoms
	"""
	#determining the risk of prostate cancer using age factor 6 . stage 1
	@Rule(Fact(Age_factor=6),Fact(psa_risk=False), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=False))
	def protocol_lowest_risk(self):
		global output, pcd_treat
		pcd_treat = "With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You are less likely to have the lowest risk of having a biopsy-detectable prostate cancer. Due to your age factor, you are at 2% risk of prostate cancer. "
		
	@Rule(Fact(Age_factor=6),Fact(psa_risk=False), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=True))
	def protocol_low_risk(self):
		global output, pcd_treat
		pcd_treat="With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You might have low risk of having a biopsy-detectable prostate cancer. Due to your age factor, you are at 2% risk of prostate cancer."
	
	
	@Rule(Fact(Age_factor=6),Fact(psa_risk=False), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=False))
	def protocol_low2_risk(self):
		global output, pcd_treat
		pcd_treat="With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
	
	#stage 2
	@Rule(Fact(Age_factor=6),Fact(psa_risk=False), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=True))
	def protocol_medl_risk(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You could have a low to medium risk of having a biopsy-detectable prostate cancer. This is  rare case and possibly could be an aggressive prostate cancer. So please see the doctor immediately for further examinations. However, due to the age factor, you have 4% risk of prostate cancer according to your age factor."
	
	
	@Rule(Fact(Age_factor=6),Fact(psa_risk=False), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=False))
	def protocol_lmed_risk(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You could have a low to medium risk of having a biopsy-detectable prostate cancer despite your age where there are rare cases of prostate cancer diagnosis. However, this is  rare case and possibly could be an aggressive prostate cancer. So please see the doctor immediately for further examinations. However, the risk of you getting a prostate cancer tumor is about 4% considering your age factor."
	
	@Rule(Fact(Age_factor=6),Fact(psa_risk=False), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=True))
	def protocol_med2_risk(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You might possibly have a medium risk of having a biopsy-detectable prostate cancer despite your age where there are rare cases of prostate cancer diagnosis. So please see the doctor immediately for further examinations. However, the risk of you getting a prostate cancer tumor is about 4% considering your age factor."
	
	#stage 3
	@Rule(Fact(Age_factor=6),Fact(psa_risk=True), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=False))
	def protocol_mhigh_risk(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You might possibly have a medium to high risk of having a prostate cancer tumor despite your age where there are rare cases of prostate cancer diagnosis. So please see the doctor immediately for further examinations. However, the risk of you getting a prostate cancer tumor is about 6%."
	
	#psa->1 
	@Rule(Fact(Age_factor=6),Fact(psa_risk=True), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=True))
	def protocol_high_risk(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You possibly have a high risk of having a biopsy-detectable prostate cancer despite your age where there are rare cases of prostate cancer diagnosis. So please see the doctor immediately for further examinations. However, according to your age factor, you could have about 6% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=6),Fact(psa_risk=True), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=False))
	def protocol_high2_risk(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You could possibly have a high risk of having a biopsy-detectable prostate cancer despite your age where there are rare cases of prostate cancer diagnosis. So please see the doctor immediately for further examinations. However, according to your age factor, you could have about 6% risk of prostate cancer." 
	
	#stage 4
	@Rule(Fact(Age_factor=6),Fact(psa_risk=True), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=True))
	def protocol_highv_risk(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You could possibly have a high to very high risk of having a biopsy-detectable prostate cancer despite your age where there are rare cases of prostate cancer diagnosis. So please see the doctor immediately for further examinations. However, according to your age factor, you could have about 8% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=6),Fact(psa_risk=True), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=False))
	def protocol_vhighl_risk(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You strongly have a very high risk of having a biopsy-detectable prostate cancer despite your age where there are rare cases of prostate cancer diagnosis. So please see the doctor immediately for further examinations. However, according to your age factor, you could have about 8% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=6),Fact(psa_risk=True), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=True))
	def protocol_vhigh2_risk(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You definitely have a very high risk of having a biopsy-detectable prostate cancer despite your age where there are rare cases of prostate cancer diagnosis. So please see the doctor immediately for further examinations. However, according to your age factor, you could have about 8% risk of prostate cancer." 
		
		
	"""=============================================================================================================================================================================="""	
	#determining the risk of prostate cancer using age factor 22
	@Rule(Fact(Age_factor=22),Fact(psa_risk=False), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=False))
	def protocol_lowest_riskb(self):
		global output, pcd_treat
		pcd_treat = "With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You are less likely to have a biopsy-detectable prostate cancer. Due to your age factor, you are at 9% risk of prostate cancer. " 
		
	
	@Rule(Fact(Age_factor=22),Fact(psa_risk=False), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=True))
	def protocol_low_riskb(self):
		global output, pcd_treat
		pcd_treat="With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You might have low risk of having a biopsy-detectable prostate cancer. Due to your age factor, you are at 9% risk of prostate cancer. " 
	
	@Rule(Fact(Age_factor=22),Fact(psa_risk=False), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=False))
	def protocol_low2_riskb(self):
		global output, pcd_treat
		pcd_treat="With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You could have low risk of having a  biopsy-detectable prostate cancer. Even though you have medium symptoms of prostate cancer check with the doctor for monitoring just in case. However, due to your age factor, you have 9% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=22),Fact(psa_risk=False), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=True))
	def protocol_medl_riskb(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You could have a low to medium risk of having a biopsy-detectable prostate cancer. This is  rare case and possibly could be an aggressive prostate cancer. So please see the doctor immediately for further examinations. However, due to the age factor, you have about 16% risk of prostate cancer according to your age factor." 
	
	@Rule(Fact(Age_factor=22),Fact(psa_risk=False), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=False))
	def protocol_lmed_riskb(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You could have a low to medium risk of having a biopsy-detectable prostate cancer. However, this is  rare case and possibly could be an aggressive prostate cancer. So please see the doctor immediately for further examinations. However, the risk of you getting a prostate cancer tumor is about 16% considering your age factor." 
	
	@Rule(Fact(Age_factor=22),Fact(psa_risk=False), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=True))
	def protocol_med2_riskb(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You might possibly have a medium risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. However, the risk of you getting a prostate cancer tumor is about 16% considering your age factor." 
	
	@Rule(Fact(Age_factor=22),Fact(psa_risk=True), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=False))
	def protocol_mhigh_riskb(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You might possibly have a medium to high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. However, the risk of you getting a prostate cancer tumor is about 22% condidering you age factor." 
	
	#psa->1
	@Rule(Fact(Age_factor=22),Fact(psa_risk=True), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=True))
	def protocol_high_riskb(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You possibly have a high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. However, according to your age factor, you have about 22% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=22),Fact(psa_risk=True), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=False))
	def protocol_high2_riskb(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You could possibly have a high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. However, according to your age factor, you have about 22% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=22),Fact(psa_risk=True), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=True))
	def protocol_highv_riskb(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You could possibly have a high to very high risk of having a biopsy-detectable prostate cancer despite your age where there are rare cases of prostate cancer diagnosis. So please see the doctor immediately for further examinations. However, according to your age factor, you have about 31% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=22),Fact(psa_risk=True), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=False))
	def protocol_vhighl_riskb(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You strongly have a very high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. However, according to your age factor, you have about 31% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=22),Fact(psa_risk=True), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=True))
	def protocol_vhigh2_riskb(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You definitely have a very high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. According to your age factor, you have about 31% risk of prostate cancer." 

	"""=============================================================================================================================================================================="""	
	#determining the risk of prostate cancer using age factor 33->medium
	@Rule(Fact(Age_factor=33),Fact(psa_risk=False), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=False))
	def protocol_lowest_riskc(self):
		global output, pcd_treat
		pcd_treat = "With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You less likely to have a low risk of having a biopsy-detectable prostate cancer. Due to your age factor, you are at 33% risk of prostate cancer. " 
		
	
	@Rule(Fact(Age_factor=33),Fact(psa_risk=False), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=True))
	def protocol_low_riskc(self):
		global output, pcd_treat
		pcd_treat="With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You might have low risk of having a biopsy-detectable prostate cancer. Due to your age factor, you are at 33% risk of prostate cancer. " 
	
	@Rule(Fact(Age_factor=33),Fact(psa_risk=False), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=False))
	def protocol_low2_riskc(self):
		global output, pcd_treat
		pcd_treat="With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You could have low risk of having a biopsy-detectable prostate cancer. Even though you have symptoms of prostate cancer check with the doctor for monitoring just in case. Due to your age factor, you have 33% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=33),Fact(psa_risk=False), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=True))
	def protocol_medl_riskc(self):
		global output
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You could have a low to medium risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. Due to the age factor, you have about 37% risk of prostate cancer according to your age factor." 
	
	@Rule(Fact(Age_factor=33),Fact(psa_risk=False), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=False))
	def protocol_lmed_riskc(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You could have a low to medium risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. The risk of you getting a prostate cancer tumor is about 42% considering your age factor." 
	
	@Rule(Fact(Age_factor=33),Fact(psa_risk=False), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=True))
	def protocol_med2_riskc(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You might possibly have a medium risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. The risk of you getting a prostate cancer tumor is about 42% considering your age factor." 
	
	@Rule(Fact(Age_factor=33),Fact(psa_risk=True), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=False))
	def protocol_mhigh_riskc(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You might possibly have a medium to high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. The risk of you getting a prostate cancer tumor is about 47% condidering you age factor." 
	
	#psa->1
	@Rule(Fact(Age_factor=33),Fact(psa_risk=True), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=True))
	def protocol_high_riskc(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You possibly have a high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. According to your age factor, you have about 52% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=33),Fact(psa_risk=True), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=False))
	def protocol_high2_riskc(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You could possibly have a high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. According to your age factor, you have about 55% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=33),Fact(psa_risk=True), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=True))
	def protocol_highv_riskc(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You could possibly have a high to very high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. According to your age factor, you have about 61% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=33),Fact(psa_risk=True), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=False))
	def protocol_vhighl_riskc(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You strongly have a very high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. According to your age factor, you have about 67% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=33),Fact(psa_risk=True), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=True))
	def protocol_vhigh2_riskc(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You definitely have a very high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. According to your age factor, you have about 73% risk of prostate cancer." 
	"""============================================================================================================================================================================="""	
	#determining the risk of prostate cancer using age factor 40->high
	@Rule(Fact(Age_factor=40),Fact(psa_risk=False), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=False))
	def protocol_lowest_riskd(self):
		global output, pcd_treat
		pcd_treat = "With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You less likely to have a low risk of having a biopsy-detectable prostate cancer. Due to your age factor, you are at 3% risk of prostate cancer. " 
		
	
	@Rule(Fact(Age_factor=40),Fact(psa_risk=False), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=True))
	def protocol_low_riskd(self):
		global output, pcd_treat
		pcd_treat="With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You might have low risk of having a biopsy-detectable prostate cancer. Due to your age factor, you are at 13% risk of prostate cancer. " 
	
	@Rule(Fact(Age_factor=40),Fact(psa_risk=False), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=False))
	def protocol_low2_riskd(self):
		global output, pcd_treat
		pcd_treat="With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You could have low risk of having a biopsy-detectable prostate cancer. Even though you have symptoms of prostate cancer check with the doctor for monitoring just in case. Due to your age factor, you have 16% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=40),Fact(psa_risk=False), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=True))
	def protocol_medl_riskd(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You could have a low to medium risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. Due to the age factor, you have about 23% risk of prostate cancer according to your age factor." 
	
	@Rule(Fact(Age_factor=40),Fact(psa_risk=False), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=False))
	def protocol_lmed_riskd(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You could have a low to medium risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. The risk of you getting a prostate cancer tumor is about 26% considering your age factor." 
	
	@Rule(Fact(Age_factor=40),Fact(psa_risk=False), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=True))
	def protocol_med2_riskd(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You might possibly have a medium risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. The risk of you getting a prostate cancer tumor is about 26% considering your age factor." 
	
	@Rule(Fact(Age_factor=40),Fact(psa_risk=True), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=False))
	def protocol_mhigh_riskd(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You might possibly have a medium to high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. The risk of you getting a prostate cancer tumor is about 30% condidering you age factor." 
	
	#psa->1
	@Rule(Fact(Age_factor=40),Fact(psa_risk=True), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=True))
	def protocol_high_riskd(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You possibly have a high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. According to your age factor, you have about 33% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=40),Fact(psa_risk=True), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=False))
	def protocol_high2_riskd(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You could possibly have a high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. According to your age factor, you have about 36% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=40),Fact(psa_risk=True), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=True))
	def protocol_highv_riskd(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You could possibly have a high to very high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. According to your age factor, you have about 39% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=40),Fact(psa_risk=True), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=False))
	def protocol_vhighl_riskd(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You strongly have a very high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. According to your age factor, you have about 43% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=40),Fact(psa_risk=True), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=True))
	def protocol_vhigh2_riskd(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You definitely have a very high risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. According to your age factor, you have about 46% risk of prostate cancer." 
	"""=============================================================================================================================================================================="""	
	#determining the risk of prostate cancer using age factor 56->veryhigh
	@Rule(Fact(Age_factor=56),Fact(psa_risk=False), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=False))
	def protocol_lowest_riske(self):
		global output, pcd_treat
		pcd_treat = "With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You are likely to have a low risk of having a biopsy-detectable prostate cancer. Due to your age factor, you are at 14% risk of prostate cancer. " 
		
	
	@Rule(Fact(Age_factor=56),Fact(psa_risk=False), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=True))
	def protocol_low_riske(self):
		global output, pcd_treat
		pcd_treat="With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You might have low risk of having a biopsy-detectable prostate cancer. Due to your age factor, you are at about 20% risk of prostate cancer. " 
	
	@Rule(Fact(Age_factor=56),Fact(psa_risk=False), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=False))
	def protocol_low2_riske(self):
		global output, pcd_treat
		pcd_treat="With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You could have low risk of having a biopsy-detectable prostate cancer tumor. Even though you have symptoms of prostate cancer check with the doctor for monitoring just in case. Due to your age factor, you have 24% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=56),Fact(psa_risk=False), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=True))
	def protocol_medl_riske(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You could have a low to medium risk of having a biopsy-detectable prostate cancer. Considering your age factor, you have about 32% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=56),Fact(psa_risk=False), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=False))
	def protocol_lmed_riske(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You could have a low to medium risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. However, the risk of you getting a prostate cancer tumor is about 34% considering your age factor." 
	
	@Rule(Fact(Age_factor=56),Fact(psa_risk=False), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=True))
	def protocol_med2_riske(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You might possibly have a medium risk of having a prostate cancer tumor despite your age where there are rare cases of prostate cancer diagnosis. So please see the doctor immediately for further examinations. However, the risk of you getting a prostate cancer tumor is about 40% considering your age factor." 
	
	@Rule(Fact(Age_factor=56),Fact(psa_risk=True), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=False))
	def protocol_mhigh_riske(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You might possibly have a medium to high risk of having a biopsy-detectable prostate cancer tumor. So please see the doctor immediately for further examinations. However, the risk of you getting a prostate cancer tumor is about 44% condidering you age factor." 
	
	#psa->1
	@Rule(Fact(Age_factor=56),Fact(psa_risk=True), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=True))
	def protocol_high_riske(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You possibly have a high risk of having a biopsy-detectable prostate cancer despited at your age you are susceptible of risk of prostate cancer. So please see the doctor immediately for further examinations. However, according to your age factor, you have about 50% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=56),Fact(psa_risk=True), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=False))
	def protocol_high2_riske(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You could possibly have a high risk of having biopsy-detectable prostate cancer tumor and at your age you're susceptible to risk of prostate cancer. So please see the doctor immediately for further examinations. Considering your age factor, you have about 54% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=56),Fact(psa_risk=True), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=True))
	def protocol_highv_riske(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You could possibly have a high to very high risk of having a prostate cancer tumor and at your age you are susceptible of biopsy-detectable prostate cancer risk. So please see the doctor immediately for further examinations. According to your age factor, you have about 58% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=56),Fact(psa_risk=True), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=False))
	def protocol_vhighl_riske(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You strongly have a very high risk of having biopsy-detectable prostate cancer tumor and at your you're susceptible of prostate cancer risk. So please see the doctor immediately for further examinations. According to your age factor, you have about 64% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=56), Fact(psa_risk=True), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=True))
	def protocol_vhigh2_riske(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You definitely have a very high risk of having a prostate cancer tumor and at your age you are susceptible of high risk of biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. According to your age factor, you have about 70% risk of prostate cancer." 
	"""=============================================================================================================================================================================="""	
	#determining the risk of prostate cancer using age factor 52->veryhigh
	@Rule(Fact(Age_factor=52),Fact(psa_risk=False), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=False))
	def protocol_lowest_riskf(self):
		global output, pcd_treat
		pcd_treat = "With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You are likely to have a low risk of having a biopsy-detectable prostate cancer. Due to your age factor, you are at 31% risk of prostate cancer. " 
		
	
	@Rule(Fact(Age_factor=52),Fact(psa_risk=False), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=True))
	def protocol_low_riskf(self):
		global output, pcd_treat
		pcd_treat="With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You might have low risk of having a biopsy-detectable prostate cancer. Due to your age factor, you are at about 31% risk of prostate cancer. " 
	
	@Rule(Fact(Age_factor=52),Fact(psa_risk=False), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=False))
	def protocol_low2_riskf(self):
		global output, pcd_treat
		pcd_treat="With stage I, you should consider the following treatment approaches:\n\n 1. Active surveillance. Your doctor tracks your PSA levels. If those levels rise, it might mean your cancer is growing or spreading. Your doctor can then change your treatment. He might also do tests like rectal exams and ultrasounds.\n\n 2. Watchful waiting. This involves fewer tests than active surveillance. Your doctor keeps a close watch on your symptoms. If you're an older man, or you have other serious health problems, your doctor might opt for this method.\n\n 3. Radiation therapy. This kills prostate cancer cells or keeps them from growing and dividing. There are two types of this treatment. The [external] kind uses a machine to aim a beam of radiation at your tumor. With [internal radiation], a doctor places radioactive pellets or seeds in or next to the tumor -- this procedure is also known as brachytherapy.\n\n 4. Radical prostatectomy. This is a surgery to remove your prostate and some of the surrounding tissue.\n\n Ablation therapy. This treatment uses freezing or high-intensity ultrasound to kill cancer cells."
		output="You could have low risk of having a biopsy-detectable prostate cancer tumor. Even though you have symptoms of prostate cancer check with the doctor for monitoring just in case. Due to your age factor, you have 37% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=52),Fact(psa_risk=False), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=True))
	def protocol_medl_riskf(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You could have a low to medium risk of having a biopsy-detectable prostate cancer. Considering your age factor, you have about 44% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=52),Fact(psa_risk=False), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=False))
	def protocol_lmed_riskf(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You could have a low to medium risk of having a biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. However, the risk of you getting a prostate cancer tumor is about 44% considering your age factor." 
	
	@Rule(Fact(Age_factor=52),Fact(psa_risk=False), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=True))
	def protocol_med2_riskf(self):
		global output, pcd_treat
		pcd_treat="With stage II, you should consider the following treatments:\n\n 1. Active surveillance. In this stage, it’s typically used if you're a much older man or you have other serious health problems.\n\n 2. Radiation therapy, possibly combined with hormone therapy. Those are drugs that stop testosterone from helping your cancer cells grow.\n\n 3. Radical prostatectomy."
		output="You might possibly have a medium risk of having a prostate cancer tumor despite your age where there are rare cases of prostate cancer diagnosis. So please see the doctor immediately for further examinations. However, the risk of you getting a prostate cancer tumor is about 47% considering your age factor." 
	
	@Rule(Fact(Age_factor=52),Fact(psa_risk=True), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=False))
	def protocol_mhigh_riskf(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You might possibly have a medium to high risk of having a biopsy-detectable prostate cancer tumor. So please see the doctor immediately for further examinations. However, the risk of you getting a prostate cancer tumor is about 57% condidering you age factor." 
	
	#psa->1
	@Rule(Fact(Age_factor=52),Fact(psa_risk=True), Fact(sympnum_pc_risk='low'), Fact(symp_prostate_cancer_att=True))
	def protocol_high_riskf(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You possibly have a high risk of having a biopsy-detectable prostate cancer despited at your age you are susceptible of risk of prostate cancer. So please see the doctor immediately for further examinations. However, according to your age factor, you have about 57% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=52),Fact(psa_risk=True), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=False))
	def protocol_high2_riskf(self):
		global output, pcd_treat
		pcd_treat="With stage III, you should consider the following treatments:\n\n 1.External radiation plus hormone therapy.\n\n 2.External radiation plus brachytherapy and possible hormone therapy.\n\n 3.Radical prostatectomy, often combined with removal of your pelvic lymph nodes. Your doctor might recommend radiation after surgery."
		output="Alert!!You could possibly have a high risk of having biopsy-detectable prostate cancer tumor and at your age you're susceptible to risk of prostate cancer. So please see the doctor immediately for further examinations. Considering your age factor, you have about 65% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=52),Fact(psa_risk=True), Fact(sympnum_pc_risk='medium'), Fact(symp_prostate_cancer_att=True))
	def protocol_highv_riskf(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You could possibly have a high to very high risk of having a prostate cancer tumor and at your age you are susceptible of biopsy-detectable prostate cancer risk. So please see the doctor immediately for further examinations. According to your age factor, you have about 70% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=52),Fact(psa_risk=True), Fact(sympnum_pc_risk='high'), Fact(symp_prostate_cancer_att=False))
	def protocol_vhighl_riskf(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		output="Alert!!You strongly have a very high risk of having biopsy-detectable prostate cancer tumor and at your you're susceptible of prostate cancer risk. So please see the doctor immediately for further examinations. According to your age factor, you have about 77% risk of prostate cancer." 
	
	@Rule(Fact(Age_factor=True),Patient(psa_risk=True), Patient(sympnum_pc_risk='high'), Patient(symp_prostate_cancer_att=True))
	def protocol_vhigh2_riskf(self):
		global output, pcd_treat
		pcd_treat="In stage 4, you should consider the following treatments:\n\n 1.Hormone therapy, which is often combined with surgery, radiation, or chemotherapy.\n\n Surgery to relieve symptoms such as bleeding or urinary obstruction and to remove cancerous lymph nodes.\n\n 2.External radiation with or without hormone therapy.\n\n 3.Chemotherapy, if standard treatments don’t relieve symptoms and the cancer continues to grow. The drugs will shrink cancer cells and slow their growth.\n\n 4.Bisphosphonate drugs, which can help slow the growth of cancer in the bone and help prevent fractures.\n\n5.The vaccine sipuleucel-T (Provenge), which boosts your immune system so it will attack the cancer cells. This might be used when hormone therapy doesn’t work.\n\n6.Palliative care, which offers you relief from symptoms like pain and trouble peeing.\n\n 7.Clinical trials are testing new treatments. They can give you state-of-the-art cancer treatments or newer ones that aren’t available yet. Ask your doctor if a clinical trial might be right for you."
		
		output="Alert!!You definitely have a very high risk of having a prostate cancer tumor and at your age you are susceptible of high risk of biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. According to your age factor, you have about 83% risk of prostate cancer." 
		
		
		
		


"""


			'freq_night_urination',
            'bloody_semen',
            'painful_urination',
            'bloody_stool',
            'weak_urine_flow',
			'painful_eju',								   
			'inad_erec',
			'erectile_dysfunc',
			'pain_in_bones',
			'swelling_lower_limbs'
"""
#symptoms input
"""
engine = InreferenceEngine()
engine.reset()
engine.declare(Patient(age=int(agevar),
					 freq_night_urination =bool(symp1),
					 bloody_semen =bool(symp2),
					 painful_urination =bool(symp3),
					 bloody_stool =bool(symp4),
					 weak_urine_flow =bool(symp5),
					 painful_eju =bool(symp6),						   
					 inad_erec =bool(symp7),
					 erectile_dysfunc =bool(symp8),
					 pain_in_bones =bool(symp9),
					 swelling_lower_limbs=bool(symp10), 
					 psa=varpsa))

engine.run()
"""


#encrypting passwords 
def encrypt_string(hash_string):
    sha_signature = \
        hashlib.md5(hash_string.encode()).hexdigest()
    return sha_signature

#database connection
conn=mysql.connector.connect(
	host="localhost",
	user="root",
	password="",
	database="pcd_db",
	buffered=True
)
	
conncursor=conn.cursor(dictionary=True)
profcursor=conn.cursor()

app = Flask(__name__)
app.secret_key = 'randompcdkey'
		
#url for main page
@app.route('/')
def main():
	#render the page login.html in a folder called templates
	return render_template("login.html")

#url for register
@app.route('/registeruser')
def reg_user():
	#render the page register.html in a folder called templates
	return render_template("register.html")
	

#url for register
@app.route('/forgotpass')
def forgot():
	#render the page register.html in a folder called templates
	return render_template("forgot-password.html")
	
#get user results
def user_res(demail):
	
	userres=None
	presql = "SELECT * FROM es_results where email='%s'"%(demail)
	conncursor.execute(presql)
	userres = conncursor.fetchall()
	return userres
	
#url for register
@app.route('/results')
def results():

	email = session['email']
	#demail='manzininin'
	userres = user_res(email)
	#render the page register.html in a folder called templates
	return render_template("results.html",userres=userres)

#url for home
@app.route('/home/')
def home():
	 
	if 'email' in session:
		email = session['email']
		return render_template("index.html")
	else:
		flash('Please login')
		return redirect(url_for('main'))
	
#url for 404
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html")
		
#url for 405
@app.errorhandler(405)
def method_not_found(e):
	return render_template("405.html")
		
#url for login which will be used on the login page as: action="/login" method ="post"
@app.route('/login/', methods=['GET', 'POST'])
def login_page():

	error = ''
	success = ''
	pda=''
	try:
		
		conncursor=conn.cursor(dictionary=True)
		if request.method == "POST":
			#declare the data posted in to variables attempted_username and attempted_password
			emailval = request.form['lemail']
			#depassval=request.form['lpassword']
			passvalp = encrypt_string(request.form['lpassword'])
			
			
			#patients
			psql="select * from patients where email='%s'"%(emailval)
			conncursor.execute(psql)
			pdata=conncursor.fetchone()
			cont = conncursor.rowcount
			pda=pdata['password']
			if passvalp == pdata["password"]:
				#setting sessions
				session['logged_in'] = True
				session['email'] = emailval
				#redirecting to the homepage after login
				
				return redirect(url_for('home'))
				
			else:
				#show error and return to the login page
				error = "Invalid credentials. Try Again. "
			
				return render_template("login.html", error = error)
			
		else:
			#show error and return to the login page
			error = "Error connecting to server."

			return render_template("login.html", error = error)
				
	except Exception as e:
		#error to recieve info and return to the login page
		error="Invalid login details. Exception: "+str(e)
		return render_template("login.html", error = error)
	
#url for entry form
@app.route('/entry/')
def entry():
	 
	if 'email' in session:
		email = session['email']
		return render_template("symptoms.html")
	else:
		flash('Please login')
		return redirect(url_for('main'))

#url for logout
@app.route('/logout/')
def logout():
	#close the sessions
	session.pop('email', None)
	return redirect(url_for('main'))

#get user data
def user_def(demail):
	
	userprof=None
	prosql = "SELECT * FROM patients where email='%s'"%(demail)
	profcursor.execute(prosql)
	userprof = profcursor.fetchone()
	return userprof
			
#url for profile
@app.route('/profile/')
def profile():
	
	if 'email' in session:
		email = session['email']
		#demail='manzininin'
		userprof = user_def(email)
		
		return render_template("profile.html", userprof=userprof)
	else:
		flash('Please login')
		return redirect(url_for('main'))
		
#edit user profile 
@app.route('/changeprof/', methods=['GET', 'POST'])
def edit_profile():

	error = ''
	success = ''
	email = session['email']
	try:
		
		if request.method == "POST":
			#declare the data posted in to variables 
			emailvap = request.form['email']
			fnamevap = request.form['fname']
			lnamevap = request.form['lname']
			dobvap = request.form['dob']
			citvap = request.form['city']
			
			#patients
			usql="update patients set firstname=%s, lastname=%s, age=%s, city=%s where email=%s"
			valu=(fnamevap, lnamevap, dobvap, citvap, emailvap)
			conncursor.execute(usql, valu)
			conn.commit()
			
			contu = conncursor.rowcount
			
			if contu > 0:
				#flash message
				flash('Profile successfully updated.')
				
				return redirect(url_for('profile'))
				
			else:
				#show error 
				flash("Error updating profile.")
			
				return redirect(url_for('profile'))
			
		else:
			#show error and return to the login page
			flash("Error connecting to server.")

			return redirect(url_for('profile'))
				
	except Exception as e:
		#error to recieve info and return to the login page
		flash('Error connecting to server.')
		return redirect(url_for('profile'))


#edit user profile 
@app.route('/changepass/', methods=['GET', 'POST'])
def change_pass():

	error = ''
	success = ''
	email = session['email']
	try:
	
		if request.method == "POST":
			#declare the data posted in to variables 
			emailpap = request.form['cemail']
			oldpassvar = encrypt_string(request.form['oldpassword'])
			newpassvar = encrypt_string(request.form['password2'])
			
			#check pass
			pasql="select password from patients where email=%s and password=%s "
			pal=(emailpap, oldpassvar)
			conncursor.execute(pasql,pal)
			pcont = conncursor.rowcount
			if pcont > 0:
				
				#password
				usql="update patients set password=%s where email=%s"
				valu=(newpassvar, emailpap)
				conncursor.execute(usql, valu)
				conn.commit()
			
				contu = conncursor.rowcount
			
				if contu > 0:
					#flash message
					flash('Profile successfully updated.')
					
					return redirect(url_for('profile'))
				
				else:
					#show error 
					error = "Error updating profile."
					
					return redirect(url_for('profile', error=error))
					
			else:
				error = "Invalid old password."
				
				return redirect(url_for('profile', error=error))
			
		else:
			#show error and return to the login page
			flash("Error connecting to server.")
			
			return redirect(url_for('profile'))
				
	except Exception as e:
		#error to recieve info and return to the login page
		flash(str(e)+"Nothing")
		
		return redirect(url_for('profile'))


def esoutput(varage,symp,symp2,symp3,symp4,symp5,symp6,symp7,symp8,symp9,symp10,vpsa):
	engine = InreferenceEngine()
	engine.reset()

	#MANUALLY ENTER THE SYMPTOMS ACCODING TO THE ORDER OF ENGINE DECLARE
	
	"""
	varage=66
	symp=False
	symp2=False
	symp3=True
	symp4=True
	symp5=True
	symp6=True
	symp7=True
	symp8=True
	symp9=True
	symp10=True
	vpsa='stable'
	"""
	engine.declare(Patient(Age = int(varage),
                        freq_night_urination=bool(symp),
                        bloody_semen= bool(symp2),
                        painful_urination= bool(symp3),
                        bloody_stool= bool(symp4),
                        weak_urine_flow= bool(symp5),
                        painful_eju =  bool(symp6),
                        inad_erec= bool(symp7),
                        erectile_dysfunc = bool(symp8),
                        pain_in_bones = bool(symp9),
                        swelling_lower_limbs = bool(symp10),
						psa = vpsa
                        ))

	engine.run()
	print(age)
	
	print(agefact)
	print(o_psa)
	print(o_num_symp)
	print("Overrally: "+output)
	print("\n Possible Treatment Suggestions: "+pcd_treat)

def dataa():
    data=esoutput()
    print(data)
#dataa()

	
#expert system inference	
@app.route('/runengine/', methods=['GET', 'POST'])
def es_engine():
	global output, age, o_psa, o_num_symp, o_bph, o_pts, agefact, pcd_treat, pcd_results
	#session.pop('res', None)
	error = ''
	success = ''
	
	try:
	
		if request.method == "POST":
			#declare the data posted in to variables
			
			engine = InreferenceEngine()
			engine.reset()
			
			
			emailr = session['email']
			agevar = request.form['age']
			symp1 = request.form['frequ']
			symp2 = request.form['semu']
			symp3 = request.form['painu']
			symp4 = request.form['blodu']
			symp5 = request.form['weaku']
			symp6 = request.form['peju']
			symp7 = request.form['inad']
			symp8 = request.form['ed']
			symp9 = request.form['painbo']
			symp10 = request.form['swell']
			varpsa = request.form['psa']
			
				 
			"""engine.declare(Patient(age=int(agevar),
					 freq_night_urination =bool(symp1),
					 bloody_semen =bool(symp2),
					 painful_urination =bool(symp3),
					 bloody_stool =bool(symp4),
					 weak_urine_flow =bool(symp5),
					 painful_eju =bool(symp6),						   
					 inad_erec =bool(symp7),
					 erectile_dysfunc =bool(symp8),
					 pain_in_bones =bool(symp9),
					 swelling_lower_limbs=bool(symp10), 
					 psa=varpsa))
					 
			engine.run()"""
			
			esoutput(agevar,symp1,symp2,symp3,symp4,symp5,symp6,symp7,symp8,symp9,symp10,varpsa)	
			
			fact_symps=["age ->"+str(agevar),
					 "freq_night_urination ->"+symp1,
					 "bloody_semen ->"+ symp2,
					 "painful_urination ->"+ symp3,
					 "bloody_stool ->"+ symp4,
					 "weak_urine_flow ->"+ symp5,
					 "painful_eju ->"+ symp6,   
					 "inad_erec ->"+ symp7,
					 "erectile_dysfunc ->"+ symp8,
					 "pain_in_bones ->"+ symp9,
					 "swelling_lower_limbs->"+ symp10, 
					 "psa ->"+varpsa]
			#storing the results
			pcd_results=(age+
			'\n '+agefact+'\n '+
			' About PSA level: \t '+o_psa+
			' About number of symptoms: 	\t\n\n '+o_num_symp+
			'\n \n  Overrally:	\t'+output)
			
			#pcd_results=session['res']
			#STORING THE TREATMENT SUGGESTIONS
			pcd_treatment=pcd_treat;
			#store the symtoms AND FACTS
			
				
			fact_array=str(fact_symps)
			fact_ara=pcd_results+output
			flash(fact_ara)
			
			# database
			if fact_array!=None:
				conncursor=conn.cursor(dictionary=True)
				#saving into database
				rinsql="INSERT INTO es_results(`email`, `results`, `symptoms`, `treatments`) VALUES(%s, %s, %s, %s)"
					
				val=(emailr, pcd_results, fact_array, pcd_treatment)
			
				conncursor.execute(rinsql, val)
				conn.commit()
				#count the rows inserted
				usercount=conncursor.rowcount
			
				if usercount > 0:
				
					success='All your symptoms have been processed.'
					#redirecting to the homepage after login
				
					return redirect(url_for('results', success=success, pcd_results=pcd_results))
					#return render_template('results.html', success=success, eng=eng)

				else:
					#show error and return to the login page
					flash("Error saving data.")

					return redirect(url_for('entry'))
			else:
				flash("Error connecting to server")
				return redirect(url_for('entry'))
				
		else:
			#show error and return to the login page
			flash("Error processing your symptoms")

			return redirect(url_for('entry'))
				
	except Exception as e:
		#error to recieve info and return to the login page
		flash(str(e)+" .Error getting data")
		
		return redirect(url_for('entry'))


"""

				if fact_array!=None:
					conncursor=conn.cursor(dictionary=True)
					#saving into database
					rinsql="INSERT INTO es_results(`email`, `results`, `symptoms`, `treatments`) VALUES(%s, %s, %s, %s)"
					
					val=(emailr, pcd_results, fact_array, pcd_treatment)
			
					conncursor.execute(rinsql, val)
					conn.commit()
					#count the rows inserted
					usercount=conncursor.rowcount
			
					if usercount > 0:
				
						success='All your symptoms have been processed.'
						#redirecting to the homepage after login
				
						return redirect(url_for('results', success=success))

					else:
						#show error and return to the login page
						flash("Error saving data.")

						return redirect(url_for('entry'))
				else:
					flash("Error connecting to server")
					return redirect(url_for('entry'))

"""

#viewing the results
@app.route('/viewresult/<idres>')
def viewresult(idres):
	
	if 'email' in session:
		email = session['email']
		
		try:
			
			val=idres
			if conn.is_connected():
				resuser=user_def(email)
				#patients
				psql="select * from es_results where id='%s'"%(val)
				conncursor.execute(psql)
				resultone=conncursor.fetchone()
			
				return render_template("viewresult.html", resultone=resultone, resuser=resuser)
				
		except Exception as e:
			#error to recieve info and return to the login page
			flash(str(e))
			return render_template("result.html")
		
	else:
		flash('Please login')
		return redirect(url_for('main'))	
		
		
#random number generation function
def rando():
	
	rnd=random.randrange(10000,99999)
	return rnd

#registration	
@app.route('/registers/', methods=[ 'GET', 'POST'])
def registers():
	
	error = ''
	success = ''
	try:
		conncursor=conn.cursor(dictionary=True)
		if request.method == "POST":
		
			#declare the data posted in to variables 
			emailval = request.form['email']
			passval = encrypt_string(request.form['password2'])
			fnameval = request.form['fname']
			lnameval = request.form['lname']
			cityval = request.form['city']
			ageval = request.form['dob']
			if emailval == None:
				error="Please fill all form fields."
				return
			else:
			
				num=rando()
				let = 'PCD'
				filenum=let+str(num)
				
				
				if conn.is_connected():
				
					y = conncursor.execute("SELECT * FROM patients WHERE email = 'emailval'")
					econt = conncursor.rowcount
					if econt > 0:
						flash("That email address is already in use.")
						return render_template('login.html')

					else:
					
						#using random numbers and characters to make an id number
						sql="select patient_fileno from patients where patient_fileno='filenum'"
						conncursor.execute(sql)
						res=conncursor.fetchone()
					if res == None:
				
						filenum=filenum
				
					else:

						fileno=res["patient_fileno"]
						while fileno==filenum:
							#rerun the random function
							num=rando()
							let = 'PCD'
							filenum=let+str(num)
							return filenum
							
					pinsql="INSERT INTO patients(patient_fileno, email, password, firstname, lastname, age, city) VALUES(%s, %s, %s, %s, %s, %s, %s)"
					vald=(filenum, emailval, passval, fnameval, lnameval, ageval, cityval)
			
					conncursor.execute(pinsql, vald)
					conn.commit()
					#count the rows inserted
					usercount=conncursor.rowcount
			
					if usercount > 0:
				
						flash('Account created successfully. Now you can login.')
						#redirecting to the homepage after login
				
						return redirect(url_for('main'))

					else:
						#show error and return to the login page
						error = "Error saving data."

						return redirect(url_for('main'))
		else:
			#show error and return to the login page
			flash("Error sending data.")

			return render_template("register.html")
				
	except Exception as e:
		#error to recieve info and return to the login page
		flash(str(e)+"Error requesting server.")
		return render_template("register.html")	
	
		
#import adminapp


#url for main page
@app.route('/adm')
def admmain():
	#render the page login.html in a folder called templates
	return render_template("admlogin.html")

#url for register
@app.route('/admregisteruser')
def admreg_user():
	#render the page register.html in a folder called templates
	return render_template("admregister.html")
	

#url for register
@app.route('/admforgotpass')
def admforgot():
	#render the page register.html in a folder called templates
	return render_template("admforgot-password.html")
	
#get user results
def admuser_res(demail):
	
	userres=None
	presql = "SELECT * FROM es_results where email='%s'"%(demail)
	conncursor.execute(presql)
	userres = conncursor.fetchall()
	return userres
	
#url for register
@app.route('/admresults')
def admresults():

	admemail = session['admin']
	
	userres = admuser_res(admemail)
	#render the page register.html in a folder called templates
	return render_template("admresults.html",userres=userres)

#MANAGING ADMINISTRATORS
#get user results
def adm_admins():
	
	userres=None
	presql = "SELECT * FROM admin"
	conncursor.execute(presql)
	adminres = conncursor.fetchall()
	return adminres
	
#url for register
@app.route('/adminview')
def adm_adminview():

	adminres = adm_admins()
	#render the page admins.html in a folder called templates
	return render_template("admins.html",adminres=adminres)

#MANAGING PATIENTS
	
#get user results
def adm_patients():
	
	patview=None
	patsql = "SELECT * FROM patients"
	conncursor.execute(patsql)
	patview = conncursor.fetchall()
	return patview
	
#url for patients
@app.route('/patientsview')
def adm_patientsview():

	patview = adm_patients()
	#render the page admpatients.html in a folder called templates
	return render_template("patients.html",patview=patview)


#deleting the patient
@app.route('/patientdel/<iddel>')
def delpatient(iddel):
	
	if 'admin' in session:
		admemail = session['admin']
		
		try:
			
			val=iddel
			if conn.is_connected():
				
				#patients
				psql="DELETE FROM `patients` WHERE `patients`.`patient_fileno`='%s'"%(val)
				conncursor.execute(psql)
				
				success="Patient file has been deleted"
				return redirect(url_for("adm_patientsview", success=success))
				
		except Exception as e:
			#error to recieve info and return to the login page
			flash(str(e))
			return redirect(url_for("adm_patientsview"))
		
	else:
		flash('Please login')
		return redirect(url_for('admmain'))	

#deleting the admin
@app.route('/admindel/<iddel>')
def deladmin(iddel):
	
	if 'admin' in session:
		admemail = session['admin']
		
		try:
			
			val=iddel
			if conn.is_connected():
				
				#admins
				psql="delete from admin where id='%s'"%(val)
				conncursor.execute(psql)
				
				success="Admin file has been deleted"
				return redirect(url_for("adm_adminview", success=success))
				
		except Exception as e:
			#error to recieve info and return to the login page
			flash(str(e))
			return redirect(url_for("adm_adminview"))
		
	else:
		flash('Please login')
		return redirect(url_for('admmain'))	
		

#url for home
@app.route('/admhome/')
def admhome():
	 
	if 'admin' in session:
		admemail = session['admin']
		return render_template("admindex.html")
	else:
		flash('Please login')
		return redirect(url_for('admmain'))
	
#url for 404
@app.errorhandler(404)
def admpage_not_found(e):
	return render_template("adm404.html")
		
#url for 405
@app.errorhandler(405)
def admmethod_not_found(e):
	return render_template("adm405.html")
		
#url for login which will be used on the login page as: action="/login" method ="post"
@app.route('/admlogin/', methods=['GET', 'POST'])
def admlogin():

	error = ''
	success = ''
	try:
		
		conncursor=conn.cursor(dictionary=True)
		if request.method == "POST":
			#declare the data posted in to variables attempted_username and attempted_password
			emailval = request.form['lemail']
			#depassval=request.form['lpassword']
			passval = encrypt_string(request.form['lpassword'])
			
			
			#patients
			psql="select * from admin where email='%s'"%(emailval)
			conncursor.execute(psql)
			pdata=conncursor.fetchone()
			cont = conncursor.rowcount
			
			if passval == pdata["password"] or pdata["userlevel"] != 1:
				#setting sessions
				session['logged_in'] = True
				session['admin'] = emailval
				#redirecting to the homepage after login
				
				return redirect(url_for('admhome'))
				
			else:
				#show error and return to the login page
				error = "Invalid credentials or You account is not yet active. Try Again. "
			
				return render_template("admlogin.html", error = error)
			
		else:
			#show error and return to the login page
			error = "Error connecting to server."

			return render_template("admlogin.html", error = error)
				
	except Exception as e:
		#error to recieve info and return to the login page
		error=e
		return render_template("admlogin.html", error = error)
	
#url for entry form
@app.route('/admentry/')
def admentry():
	 
	if 'admin' in session:
		admemail = session['admin']
		return render_template("admsymptoms.html")
	else:
		flash('Please login')
		return redirect(url_for('admmain'))

#url for logout
@app.route('/admlogout/')
def admlogout():
	#close the sessions
	session.pop('admin', None)
	return redirect(url_for('admmain'))

#get user data
def admuser_def(demail):
	
	userprof=None
	prosql = "SELECT * FROM admin where email='%s'"%(demail)
	profcursor.execute(prosql)
	userprof = profcursor.fetchone()
	return userprof
			
#url for profile
@app.route('/admprofile/')
def admprofile():
	
	if 'admin' in session:
		admemail = session['admin']
		#demail='manzininin'
		userprof = admuser_def(admemail)
		
		return render_template("admprofile.html", userprof=userprof)
	else:
		flash('Please login')
		return redirect(url_for('admmain'))
		
#edit user profile 
@app.route('/admchangeprof/', methods=['GET', 'POST'])
def admedit_profile():

	error = ''
	success = ''
	admemail = session['admin']
	try:
		
		if request.method == "POST":
			#declare the data posted in to variables 
			emailvap = request.form['email']
			fnamevap = request.form['fname']
			lnamevap = request.form['lname']
			dobvap = request.form['dob']
			citvap = request.form['city']
			
			#patients
			usql="update admin set firstname=%s, lastname=%s, age=%s, city=%s where email=%s"
			valu=(fnamevap, lnamevap, dobvap, citvap, emailvap)
			conncursor.execute(usql, valu)
			conn.commit()
			
			contu = conncursor.rowcount
			
			if contu > 0:
				#flash message
				flash('Profile successfully updated.')
				
				return redirect(url_for('admprofile'))
				
			else:
				#show error 
				flash("Error updating profile.")
			
				return redirect(url_for('admprofile'))
			
		else:
			#show error and return to the login page
			flash("Error connecting to server.")

			return redirect(url_for('admprofile'))
				
	except Exception as e:
		#error to recieve info and return to the login page
		flash('Error connecting to server.')
		return redirect(url_for('admprofile'))
		

#edit user password
@app.route('/admchangepass/', methods=['GET', 'POST'])
def admchange_pass():

	error = ''
	success = ''
	admemail = session['admin']
	try:
	
		if request.method == "POST":
			#declare the data posted in to variables 
			emailpap = request.form['cemail']
			oldpassvar = encrypt_string(request.form['oldpassword'])
			newpassvar = encrypt_string(request.form['password2'])
			
			#check pass
			pasql="select password from admin where email=%s and password=%s "
			pal=(emailpap, oldpassvar)
			conncursor.execute(pasql,pal)
			pcont = conncursor.rowcount
			if pcont > 0:
				
				#password
				usql="update admin set password=%s where email=%s"
				valu=(newpassvar, emailpap)
				conncursor.execute(usql, valu)
				conn.commit()
			
				contu = conncursor.rowcount
			
				if contu > 0:
					#flash message
					flash('Profile successfully updated.')
					
					return redirect(url_for('admprofile'))
				
				else:
					#show error 
					error = "Error updating profile."
					
					return redirect(url_for('admprofile', error=error))
					
			else:
				error = "Invalid old password."
				
				return redirect(url_for('admprofile', error=error))
			
		else:
			#show error and return to the login page
			flash("Error connecting to server.")
			
			return redirect(url_for('admprofile'))
				
	except Exception as e:
		#error to recieve info and return to the login page
		flash(str(e)+"Nothing")
		
		return redirect(url_for('admprofile'))

#edit userlevel
@app.route('/admactivate', methods=['GET', 'POST'])
def admuserlevel():

	error = ''
	success = ''
	admemail = session['admin']
	
	try:
	
		if request.method == "POST":
			#declare the data posted in to variables 
			empnum = request.form['empnum']
			userlvl = request.form['userlvl']
			
			#password
			usql="update admin set userlevel=%s where employeeid=%s"
			valu=(userlvl, empnum)
			conncursor.execute(usql, valu)
			conn.commit()
			
			contu = conncursor.rowcount
			
			if contu > 0:
				#flash message
				flash('Userlevel successfully updated.')
					
				return redirect(url_for('adm_adminview'))
				
			else:
				#show error 
				error = "Error updating userlevel."
					
				return redirect(url_for('adm_adminview', error=error))
					
		else:
		
			flash("Error connecting to server.")
				
			return redirect(url_for('adm_adminview', error=error))
				
	except Exception as e:
		#error to recieve info and return to the login page
		flash(str(e))
		
		return redirect(url_for('adm_adminview'))



#viewing the results
@app.route('/admviewresult/<idres>')
def admviewresult(idres):
	
	if 'admin' in session:
		admemail = session['admin']
		
		try:
			
			val=idres
			if conn.is_connected():
				resuser=admuser_def(admemail)
				#patients
				psql="select * from es_results where id='%s'"%(val)
				conncursor.execute(psql)
				resultone=conncursor.fetchone()
			
				return render_template("admviewresult.html", resultone=resultone, resuser=resuser)
				
		except Exception as e:
			#error to recieve info and return to the login page
			flash(str(e))
			return render_template("admresult.html")
		
	else:
		flash('Please login')
		return redirect(url_for('admmain'))	
		
		
#random number generation function
def admrando():
	
	rnd=random.randrange(10000,99999)
	return rnd

#registration	
@app.route('/admregister', methods=['GET','POST'])
def admregister():

	error = ''
	success = ''
	try:
	
		if request.method == "POST":
			
			#declare the data posted in to variables 
			emailvar = request.form['email']
			passvar = encrypt_string(request.form['password2'])
			fnamevar = request.form['fname']
			lnamevar = request.form['lname']
			addvar = request.form['address']
			agevar = request.form['dob']
			if emailvar=="":
				error="Please fill all form fields."
				return
			else:
			
				num=rando()
				let = 'PCD'
				filenum=let+str(num)
				
				
				if conn.is_connected():
				
					x = conncursor.execute("SELECT * FROM admin WHERE email = 'emailval'")
					econt = conncursor.rowcount
					if econt > 0:
						flash("That email address is already in use.")
						return render_template('admlogin.html')

					else:
					
						#using random numbers and characters to make an id number
						sql="select employeeid from admin where employeeid='filenum'"
						conncursor.execute(sql)
						res=conncursor.fetchone()
					if res == None:
				
						filenum=filenum
				
					else:

						fileno=res["employeeid"]
						while fileno==filenum:
							#rerun the random function
							num=rando()
							let = 'PCD'
							filenum=let+str(num)
							return filenum
					insql="INSERT INTO admin(employeeid, email, password, firstname, lastname, age, address) VALUES(%s, %s, %s, %s, %s, %s, %s)"
					val=(filenum, emailvar, passvar, fnamevar, lnamevar, agevar, addvar)
			
					conncursor.execute(insql, val)
					conn.commit()
					#count the rows inserted
					usercount=conncursor.rowcount
			
					if usercount > 0:
				
						success='Account created successfully. Now you can login.'
						#redirecting to the homepage after login
						return render_template('admlogin.html')
						#return redirect(url_for('admmain', success = success))
						
						
					else:
						#show error and return to the login page
						error = "Error saving data."
						#return render_template('admregister.html')
						return redirect(url_for('admreg_user', error=error))
		else:
			flash('Error sending data')
			return render_template('admregister.html')
						
	except Exception as e:
		#error to recieve info and return to the login page
		flash(str(e)+" .Error getting data")
		#return render_template('admregister.html')
		return redirect(url_for('admreg_user'))				


@app.route('/admrunengine/', methods=['GET', 'POST'])
def admes_engine():
	global output, age, o_psa, o_num_symp, o_bph, o_pts, agefact, pcd_treat, pcd_results
	#session.pop('res', None)
	error = ''
	success = ''
	
	try:
	
		if request.method == "POST":
			#declare the data posted in to variables
			
			engine = InreferenceEngine()
			engine.reset()
			
			
			emailr = session['admin']
			agevar = request.form['age']
			symp1 = request.form['frequ']
			symp2 = request.form['semu']
			symp3 = request.form['painu']
			symp4 = request.form['blodu']
			symp5 = request.form['weaku']
			symp6 = request.form['peju']
			symp7 = request.form['inad']
			symp8 = request.form['ed']
			symp9 = request.form['painbo']
			symp10 = request.form['swell']
			varpsa = request.form['psa']
			
				 
			"""engine.declare(Patient(age=int(agevar),
					 freq_night_urination =bool(symp1),
					 bloody_semen =bool(symp2),
					 painful_urination =bool(symp3),
					 bloody_stool =bool(symp4),
					 weak_urine_flow =bool(symp5),
					 painful_eju =bool(symp6),						   
					 inad_erec =bool(symp7),
					 erectile_dysfunc =bool(symp8),
					 pain_in_bones =bool(symp9),
					 swelling_lower_limbs=bool(symp10), 
					 psa=varpsa))
					 
			engine.run()"""
			
			esoutput(agevar,symp1,symp2,symp3,symp4,symp5,symp6,symp7,symp8,symp9,symp10,varpsa)	
			
			fact_symps=["age ->"+str(agevar),
					 "freq_night_urination ->"+symp1,
					 "bloody_semen ->"+ symp2,
					 "painful_urination ->"+ symp3,
					 "bloody_stool ->"+ symp4,
					 "weak_urine_flow ->"+ symp5,
					 "painful_eju ->"+ symp6,   
					 "inad_erec ->"+ symp7,
					 "erectile_dysfunc ->"+ symp8,
					 "pain_in_bones ->"+ symp9,
					 "swelling_lower_limbs->"+ symp10, 
					 "psa ->"+varpsa]
			#storing the results
			pcd_results=(age+
			'\n '+agefact+'\n '+
			' About PSA level: \t '+o_psa+
			' About number of symptoms: 	\t\n\n '+o_num_symp+
			'\n \n  Overrally:	\t'+output)
			
			#pcd_results=session['res']
			#STORING THE TREATMENT SUGGESTIONS
			pcd_treatment=pcd_treat;
			#store the symtoms AND FACTS
			
				
			fact_array=str(fact_symps)
			fact_ara=pcd_results+output
			flash(fact_ara)
			
			# database
			if fact_array!=None:
				conncursor=conn.cursor(dictionary=True)
				#saving into database
				rinsql="INSERT INTO es_results(`email`, `results`, `symptoms`, `treatments`) VALUES(%s, %s, %s, %s)"
					
				val=(emailr, pcd_results, fact_array, pcd_treatment)
			
				conncursor.execute(rinsql, val)
				conn.commit()
				#count the rows inserted
				usercount=conncursor.rowcount
			
				if usercount > 0:
				
					success='All your symptoms have been processed.'
					#redirecting to the homepage after login
				
					return redirect(url_for('admresults', success=success, pcd_results=pcd_results))
					#return render_template('results.html', success=success, eng=eng)

				else:
					#show error and return to the login page
					flash("Error saving data.")

					return redirect(url_for('admentry'))
			else:
				flash("Error connecting to server")
				return redirect(url_for('admentry'))
				
		else:
			#show error and return to the login page
			flash("Error processing your symptoms")

			return redirect(url_for('admentry'))
				
	except Exception as e:
		#error to recieve info and return to the login page
		flash(str(e)+" .Error getting data")
		
		return redirect(url_for('admentry')) 

		

if __name__ == "__main__":
	
	
	app.run(debug=True, host='127.0.0.1', port=4001)	
	
	
	