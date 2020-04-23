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
	@Rule(Patient(psa=MATCH.psa))
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
		print("Helloefjehuieq7gihyewqo8yq28uiy")
		output="Alert!!You definitely have a very high risk of having a prostate cancer tumor and at your age you are susceptible of high risk of biopsy-detectable prostate cancer. So please see the doctor immediately for further examinations. According to your age factor, you have about 83% risk of prostate cancer." 
		print(output)
		#out=output+".TREATMENTS \n\n"+pcd_treat
		
		
		


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
pes=''
def es_output(agevar,symp1,symp2,symp3,symp4,symp5,symp6,symp7,symp8,symp9,symp10,varpsa):
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

	pes=engine.run()
	
	return pes
