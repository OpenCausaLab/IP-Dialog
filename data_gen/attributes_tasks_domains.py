import random

attribute_dict = {
    "age": ["child", "teenager", "young_adult", "adult", "middle-aged", "elderly"],
    "income_level": ["low_income", "middle_income", "high_income"],
    "profession": ["student", "teacher", "sales_worker", "office_clerk", "factory_worker", "software_engineer", "healthcare_worker", "driver", "farmer", "cook", "cleaner", "journalist", "retiree", "entrepreneur",],
    "openness": ["high", "low"],
    "conscientiousness": ["high", "low"],
    "extraversion": ["high", "low"],
    "agreeableness": ["high", "low"],
    "neuroticism": ["high", "low"],
    "residence": ["urban", "rural"],
    "gender": ["male", "female"],
    "health": ["healthy", "minor_issue", "disabled"],
    "hobby": ["reading", "cooking", "photography", "sports", "gaming", "movies", "travel", "music", "crafts"]
}

task_info = {
########################################
"recommend": {"description":"recommend products based on the needs of a user's specific attribute.",
"domains":["Sports", "Health", "Medical Care", "Travel", "Transportation", "Education", "Career Related Products", "Interpersonal Relationships", "Consumption", "Entertainment", "Media", "News", "Fashion and Style", "Tech Products"],
# <subject generation>
"example_domain": "Education",
"example_subjects": '''- courses
- study tips
''',
# <request generation>
"example_user_attribute_group": '''{"age": "adult", "gender": "female", "income_level": "middle_income", "profession": "cook", "openness": "low", "conscientiousness": "high", "extraversion": "high", "agreeableness": "low", "neuroticism": "high", "residence": "rural", "health": "minor_issue", "hobby": "cooking"}''',
"example_subject": "courses",
"example_requests": '''- I want to learn some online courses. What do you recommend?
- I need resources to prepare for my courses. Can you recommend some?
- I want to learn French offline. Do you know any paricular course types that fit?
''',
"mention_attr": True,
# <answer generation>
"example_request_and_response": '''User: I want to learn some online courses for my health. What do you recommend?
Output: - Attributes: [profession: cook, openness: low, conscientiousness: high, hobby: cooking]
- Analysis: [These attributes indicate a need for culinary-focused, structured courses. Low openness suggests practical options aligned with current skills. High conscientiousness implies preference for certified programs. ]
- Answer: [Advanced Culinary Techniques, Food Safety Certification, Time Management for Chefs]''', 
"answer_note": "Extract only the attributes that influence the recommendation. For some categories such as clothing, you may need to consider gender and age.",
},
########################################
"rank": {"description":"rank a series of given items according to the user's potential level of interest.",
"domains":["Sports", "Health", "Medical Care", "Travel", "Transportation", "Education", "Career Related Products", "Interpersonal Relationships", "Consumption", "Entertainment", "Media", "News", "Fashion and Style", "Tech Products"],
# <subject generation>
"example_domain": "Education",
"example_subjects": '''- courses
- study tips
- learning platforms
''',
# <request generation>
"example_subject": "courses",
"example_user_attribute_group": '''{"age": "adult", "gender": "female", "income_level": "middle_income", "profession": "cook", "openness": "low", "conscientiousness": "high", "extraversion": "high", "agreeableness": "low", "neuroticism": "high", "residence": "rural", "health": "minor_issue", "hobby": "cooking"}''',
"example_requests": '''- Please rank the following online courses in order of suitability for me: A. online music course B. online painting course C. online cooking course D. online language course [Answer: CDAB]''',
"task_specific_note": "Give your answer after the user request. Do not generate options that are hard to rank.",
"mention_attr": True,
# <answer generation>
"example_request_and_response": '''User: Please rank the following online courses in order of suitability for me: A. online music course B. online painting course C. online cooking course D. online language course
Output: - Attributes: [profession: cook, openness: low, hobby: cooking, conscientiousness: high, extraversion: high]
- Analysis: [Given the user's profession as a cook, cooking hobby, and low openness, courses closely related to their current interests and skills would be most suitable. High conscientiousness indicates a preference for structured learning, while high extraversion suggests a preference for interactive courses.]
- Answer: [C, D, A, B]''',},
########################################
"filter": {"description":"filter a given list of items based on user attributes and preferences, retaining suitable content and removing irrelevant items. ",
"domains":["Sports", "Health", "Medical Care", "Travel", "Transportation", "Education", "Career Related Products", "Interpersonal Relationships", "Consumption", "Entertainment", "Media", "News", "Fashion and Style", "Tech Products"],
# <subject generation>
"example_domain": "Education",
"example_subjects": '''- courses
- study tips
''',
# <request generation>
"example_subject": "courses",
"example_requests": '''- Please filter through the following online courses and leave only those most suitable for me: A. online music course B. online painting course C. online cooking course D. online language course E. online coding course [Answer: CD]
''',
"mention_attr": True,
"task_specific_note": "Make sure there is less than 2 items left after filtering. Give your answer after the user request.",
# <answer generation>
"example_user_attribute_group": '''{"age": "adult", "gender": "female", "income_level": "middle_income", "profession": "cook", "openness": "low", "conscientiousness": "high", "extraversion": "high", "agreeableness": "low", "neuroticism": "high", "residence": "rural", "health": "minor_issue", "hobby": "cooking"}''',
"example_request_and_response": '''User: Please filter through the following online courses and leave only those most suitable for me: A. online music course B. online painting course C. online cooking course D. online language course E. online coding course
Output: - Attributes: [profession: cook, openness: low, hobby: cooking]
- Analysis: [The user's profession as a cook and hobby of cooking strongly favors culinary courses. Low openness suggests preference for familiar subjects, supporting cooking-related options.]
- Answer: [C]''',
"answer_note": "Make sure there is no more than 2 item left after filtering.",
},
########################################
"predict": {"description":"predict whether a user will take a specific action or make a particular decision.",
"domains":["Sports", "Health", "Medical Care", "Travel", "Transportation", "Education", "Career", "Interpersonal Relationships", "Consumption", "Entertainment", "Media", "News", "Fashion and Style", "Engagement", "Financial Investment"],
# <subject generation>
"example_domain": "Education",
"example_subjects": '''- enrolling in an online course
- pursuing a graduate degree
- participating in a school fundraising event
''',
# <request generation>
"example_subject": "enrolling in an online course",
"example_requests": '''- Predict whether I will enroll in an online course for cooking [Answer: Yes, Reason: According to your profession, you might be.]
- Predict whether I will enroll in an online course for marathon. [Answer: No, Reason: According to your low openness and health situation, you probably will not enroll.]
''',
"mention_attr": True,
"example_user_attribute_group": '''{"age": "adult", "gender": "female", "income_level": "middle_income", "profession": "cook", "openness": "low", "conscientiousness": "high", "extraversion": "high", "agreeableness": "low", "neuroticism": "high", "residence": "rural", "health": "minor_issue", "hobby": "cooking"}''',
"task_specific_note": "- Give your answer after the user request. The requests should be designed containing both yes and no answers.",
# <answer generation>
"example_request_and_response": '''User: Predict whether I will enroll in an online course for cooking.
Output: 
- Attributes: [profession: cook, openness: low, conscientiousness: high, residence: rural, hobby: cooking]
- Analysis: [Your role as a cook, hobby of cooking and high conscientiousness suggest interest in professional growth. Low openness may resist online learning, but rural residence makes it practical. High conscientiousness likely outweighs low openness for career advancement.]
- Answer: [yes]''',
"answer_note":"your Answer should include yes and no only.",
},
########################################
"preference_infer": {"description":"infer the type or characteristics of objects an individual prefers based on their attributes. This involves understanding their general preferences rather than identifying specific items they might like.",
"domains":["Sports", "Health", "Medical Care", "Travel", "Transportation", "Education", "Career", "Interpersonal Relationships", "Consumption", "Time Management", "Psychological Counseling", "Entertainment", "Media", "News", "Product Marketing", "Advertising", "Fashion and Style"],
# <subject generation>
"example_domain": "Education",
"example_subjects": '''- courses
- study tips
- learning platforms
''',
# <request generation>
"example_subject": "courses",
"example_user_attribute_group": '''{"age": "adult", "gender": "female", "income_level": "middle_income", "profession": "cook", "openness": "low", "conscientiousness": "high", "extraversion": "high", "agreeableness": "low", "neuroticism": "high", "residence": "rural", "health": "minor_issue", "hobby": "cooking"}''',
"example_requests": '''- What kind of courses do I prefer? A. Theoretical B. Creative C. Practical D. Academic [Answer: C. Practical. This aligns with your profession as a cook, high conscientiousness, low openness, and rural residence, all suggesting a preference for immediately applicable skills and knowledge.]''',
"mention_attr": True,
"task_specific_note": "Give your answer after the user request. Your options should describe the characteristics instead of specific objects",
# <answer generation>
"example_request_and_response": '''User: What kind of courses do I prefer? A. Theoretical B. Creative C. Practical D. Academic
Output: - Attributes: [profession: cook, openness: low, conscientiousness: high, residence: rural]
- Analysis: [Your profession as a cook and high conscientiousness suggest a preference for practical, immediately applicable skills. Low openness may resist theoretical or abstract concepts, while rural residence favors hands-on learning.]
- Answer: [C]''',
"answer_note":"You can choose 1,2 or 3 options in your Answer. Make sure they best satisfy what the user prefers most.",
},
########################################
"risk_detect": {"description":"detect potential risks that a user with the given attributes may face.",
# <answer generation>
"example_user_attribute_group": '''{"age": "adult", "gender": "female", "income_level": "middle_income", "profession": "cook", "openness": "low", "conscientiousness": "high", "extraversion": "high", "agreeableness": "low", "neuroticism": "high", "residence": "rural", "health": "minor_issue", "hobby": "cooking"}''',
"example_request_and_response": '''User: What risks do you think I might face?
Output: - Attributes: [profession: cook, health: minor_issue, residence: rural, neuroticism: high, hobby: cooking].
- Analysis: [Cook profession implies occupational hazards. Rural residence suggests limited healthcare access. Minor health issue could worsen. High neuroticism may increase stress.]
- Answer: [1. Kitchen injuries (burns, cuts) 2. Delayed medical care in rural area 3. Work-related stress aggravating health issue 4. Anxiety due to high neuroticism]''',
"answer_note":"List the risks with numbers in your Answer.",
}, 
########################################
"intention_infer": {"description":"infer the exact intentions of a user with specific attributes given an implicit user request.",
"domains":["Sports", "Health", "Medical Care", "Travel", "Transportation", "Education", "Career", "Interpersonal Relationships", "Consumption", "Time Management", "Psychological Counseling", "Entertainment"],
# <subject generation>
"example_domain": "Education",
"example_subjects": '''- courses
- study tips
- learning platforms
''',
# <request generation>
"example_subject": "courses",
"example_user_attribute_group": '''{"age": "adult", "gender": "female", "income_level": "middle_income", "profession": "cook", "openness": "low", "conscientiousness": "high", "extraversion": "high", "agreeableness": "low", "neuroticism": "high", "residence": "rural", "health": "minor_issue", "hobby": "music"}''',
"example_requests": '''- Please infer my full intention for learning online courses. [Answer: Based on your profession as a cook, high conscientiousness, and high extraversion, you may want to learn courses that can be immediately applied to your work and life.]''',
"mention_attr": True,
"task_specific_note": "- Give your answer after the user request.",
# <answer generation>
"example_request_and_response": '''User: Please infer my full intention for learning online courses.
Output: - Attributes: [profession: cook, conscientiousness: high, health: minor_issue, residence: rural]
- Analysis: [As a cook with high conscientiousness, you likely aim for professional growth. Your minor health issue and rural residence suggest a preference for convenient, accessible learning options.]
- Answer: [1. Enhance your culinary skills 2. Leverage the flexibility of online learning for rural and health accommodations.]''',
"answer_note":"Extract only the attributes that influence the intention infer. List the intentions with numbers in your Answer.",
},
########################################
"advice": {"description":"provide actionable advice to the user. Offer specific methods to address their problem.",
"domains":["Sports", "Health", "Medical Care", "Travel", "Transportation", "Education", "Career", "Interpersonal Relationships", "Consumption", "Time Management", "Psychological Counseling", "Entertainment"],
# <subject generation>
"example_domain": "Education",
"example_subjects": '''- review
- teaching
- learning
''',
# <request generation>
"example_subject": "review",
"example_user_attribute_group": '''{"age": "adult", "gender": "female", "income_level": "middle_income", "profession": "cook", "openness": "low", "conscientiousness": "high", "extraversion": "high", "agreeableness": "low", "neuroticism": "high", "residence": "rural", "health": "minor_issue", "hobby": "movies"}''',
"example_requests": '''- I need advice on how to review my course. [Answer: Based on your profession as a cook, high conscientiousness, and high extraversion, you may want to review your course in a practical way, such as cooking the dishes you learned in the course.]''',
"mention_attr": True,
"task_specific_note": "- Respond to the user's request with actionable advice. Offer a specific method or step to address their problem rather than suggesting an object.",
# <answer generation>
"example_request_and_response": '''User: I need advice on how to review my course.
Output: - Attributes: [profession: cook, conscientiousness: high, residence: rural, health: minor_issue]
- Analysis: [Cook with high conscientiousness needs efficient, home-based study methods due to rural location and health concerns.]
- Answer: [1. Set up a dedicated study space at home. 2. Create a detailed, week-by-week review plan. 3. Use online resources for remote learning. 4. Incorporate course material into daily cooking routine. 5. Take regular breaks to address health needs.]''',
"answer_note":"Extract only the attributes that influence the advice. Respond to the user's request with actionable advice. Offer a specific method or step to address their problem rather than suggesting an object. List the advices with numbers in your Answer.",
},
########################################
# "plan": {"description":"generate a personalized plan for the user. Summarize key points based on user attributes, then provide the plan. The ultimate goal is to outline specific action steps that will help achieve the predetermined outcomes.",
# "domains":["Sports", "Health", "Medical Care", "Travel", "Transportation", "Education", "Career", "Interpersonal Relationships", "Consumption", "Time Management", "Psychological Counseling", "Entertainment"],
# # <subject generation>
# "example_domain": "Education",
# "example_subjects": '''- courses selection
# - study schedule
# - university application plan
# ''',
# # <request generation>
# "example_subject": "courses selection",
# "example_user_attribute_group": '''{"age": "adult", "gender": "female", "income_level": "middle_income", "profession": "cook", "openness": "low", "conscientiousness": "high", "extraversion": "high", "agreeableness": "low", "neuroticism": "high", "residence": "rural", "health": "minor_issue", "hobby": "travel"}''',
# "example_requests": '''- I need to select a few courses to improve my skills in 3 months for my test. I also have work to do during the day. Please plan a schedule for me. [Plan Related Attributes: Cook in rural area, middle income, extroverted, busy schedule.
# Plan: Enroll in flexible online culinary course (4 hours/week). Join monthly virtual chef networking group. Use daily cooking app for quick skill tips (15 mins/day).]''',
# "mention_attr": True,
# "task_specific_note": "- Give your answer after the user request.",
# # <answer generation>
# "example_request_and_response": '''User: I need to select a few courses to improve my skills in 3 months for my test. I also have work to do during the day. Please plan a schedule for me.
# Output: - Attributes: [profession: cook, conscientiousness: high, residence: rural, health: minor_issue, income_level: middle_income]
# - Analysis: [As a cook with high conscientiousness, you'll benefit from a structured learning approach. Rural location limits in-person options, suggesting online courses. Health issues and middle income indicate need for flexible, cost-effective solutions.]
# - Answer: [1. structured learning 2. online courses is better 3. flexible, cost-effective solutions]
# - Plan: [Enroll in flexible online culinary course (4 hours/week). Join monthly virtual chef networking group. Use daily cooking app for quick skill tips (15 mins/day).]''',
# "answer_note":"Your answer should about the specific requierments for the plan for the user. List your requirements with numbers in your Answer. Your plan should be concise and clear.",
# "additional_output": "- Plan: [...]."
# },
########################################
"decision": {"description":"make a decision for a user on whether to perform an action or not.",
"domains":["Sports", "Health", "Medical Care", "Travel", "Transportation", "Financial Investment", "Education", "Career", "Interpersonal Relationships", "Consumption", "Time Management", "Entrepreneurship and Business"],
# <subject generation>
"example_domain": "Education",
"example_subjects": '''- whether to pursue a graduate degree
- acceptance of university offer
- choice of major
''',
# <request generation>
"example_subject": "whether to pursue a graduate degree",
"example_user_attribute_group": '''{"age": "adult", "gender": "female", "income_level": "middle_income", "profession": "cook", "openness": "low", "conscientiousness": "high", "extraversion": "high", "agreeableness": "low", "neuroticism": "high", "residence": "rural", "health": "minor_issue", "hobby": "cooking"}''',
"example_requests": '''- Should I pursue a graduate degree in music? [Related Attributes: no music background, high conscientiousness, low openness, rural residence, minor health issue. Answer: No. Reason: Based on your current situation, it may not be the best choice for you.]''',
"mention_attr": True,
"task_specific_note": "- Give your answer after the user request. Your user request should not contain any hints about the attributes. It should be hard to make a decision.",
# <answer generation>
"example_request_and_response": '''User: Should I pursue a graduate degree in music?
- Attributes: [profession: cook, openness: low, conscientiousness: high, residence: rural].
- Analysis: [As a cook with low openness, pursuing a graduate degree in music represents a significant departure from the user's current profession and comfort zone. High conscientiousness suggests dedication to current work. Rural residence could limit access to music education opportunities.]
- Answer: [no]''',
"answer_note":"Your answer should be either yes or no.",
},
########################################
"convince": {"description":"convince a user to do something.",
"domains":["Sports", "Health", "Medical Care", "Entertainment", "Media", "Travel", "Transportation", "Environmental Protection", "Financial Investment", "Education", "Career", "Product Marketing", "Social Welfare", "Technology Adoption", "Psychological Counseling"],
# <subject generation>
"example_domain": "Education",
"example_subjects": '''- continue learning
- take a course
- study hard
''',
# <request generation>
"example_subject": "continue learning",
"example_user_attribute_group": '''{"age": "adult", "gender": "female", "income_level": "middle_income", "profession": "cook", "openness": "low", "conscientiousness": "high", "extraversion": "high", "agreeableness": "low", "neuroticism": "high", "residence": "rural", "health": "minor_issue", "hobby": "music"}''',
"example_requests": '''- Convince me to take a course on cooking. [Related Attributes: cook, rural residence, middle income, high conscientiousness, high extraversion. Answer: You should take a course on cooking to improve your skills and meet other chefs. It will help you grow your career and make new friends.],''',
"mention_attr": True,
"task_specific_note": "Give your answer after the user request.",
# <answer generation>
"example_request_and_response": '''User: Convince me to take a course on cooking.
Attributes: [profession: cook, conscientiousness: high, health: minor_issue, income_level: middle_income].
Analysis: As a cook with high conscientiousness, the user likely values skill improvement and professional development. The minor health issue and middle income level indicate potential benefits from learning healthier, cost-effective cooking techniques.
Answer: [As a dedicated cook, you understand the importance of continually honing your craft. A specialized cooking course could be the perfect opportunity to elevate your skills and stay ahead in your profession. Not only could this course help you create healthier dishes to support your well-being, but it might also teach you cost-effective methods to maximize your ingredients, saving you money in the long run.]''',
"answer_note":"Extract only the attributes that influence your convincing.",
},
}

# total number: 166320
def get_proper_attribue_group(attribute_dict=attribute_dict):
    """
    Get the proper attribute group for the dataset generation.
    """
    attribute_groups = []
    for age in attribute_dict["age"]:
        # child or teenager
        if age == "child" or age == "teenager":
            for gender in attribute_dict["gender"]:
                income_level = "low_income"
                profession = "student"
                for openness in attribute_dict["openness"]:
                    for conscientiousness in attribute_dict["conscientiousness"]:
                        for extraversion in attribute_dict["extraversion"]:
                            for agreeableness in attribute_dict["agreeableness"]:
                                for neuroticism in attribute_dict["neuroticism"]:
                                    for residence in attribute_dict["residence"]:
                                        
                                        health_prob = random.random()
                                        if health_prob < 0.7:
                                            health = "healthy"
                                        elif health_prob < 0.9:
                                            health = "minor_issue"
                                        else:
                                            health = "disabled"
                                        
                                        for hobby in attribute_dict["hobby"]:
                        
                                            attribute_group_item = {
                                                "age": age,
                                                "gender": gender,
                                                "income_level": income_level,
                                                "profession": profession,
                                                "openness": openness,
                                                "conscientiousness": conscientiousness,
                                                "extraversion": extraversion,
                                                "agreeableness": agreeableness,
                                                "neuroticism": neuroticism,
                                                "residence": residence,
                                                "health": health,
                                                "hobby": hobby
                                            }
                                            attribute_groups.append(attribute_group_item)
        elif age == "elderly":
            for gender in attribute_dict["gender"]:
                income_level = "low_income"
                profession = "retiree"
                for openness in attribute_dict["openness"]:
                    for conscientiousness in attribute_dict["conscientiousness"]:
                        for extraversion in attribute_dict["extraversion"]:
                            for agreeableness in attribute_dict["agreeableness"]:
                                for neuroticism in attribute_dict["neuroticism"]:
                                    for residence in attribute_dict["residence"]:
                                        
                                        health_prob = random.random()
                                        if health_prob < 0.7:
                                            health = "healthy"
                                        elif health_prob < 0.9:
                                            health = "minor_issue"
                                        else:
                                            health = "disabled"
                                            
                                        for hobby in attribute_dict["hobby"]:
                                            attribute_group_item = {
                                                "age": age,
                                                "gender": gender,
                                                "income_level": income_level,
                                                "profession": profession,
                                                "openness": openness,
                                                "conscientiousness": conscientiousness,
                                                "extraversion": extraversion,
                                                "agreeableness": agreeableness,
                                                "neuroticism": neuroticism,
                                                "residence": residence,
                                                "health": health,
                                                "hobby": hobby
                                            }
                                            attribute_groups.append(attribute_group_item)
                                
                
        elif age == "young adult":
            for gender in attribute_dict["gender"]:
                for profession in attribute_dict["profession"]:
                    if profession == "retiree":
                        continue
                    for income_level in attribute_dict["income_level"]:
                        for openness in attribute_dict["openness"]:
                            for conscientiousness in attribute_dict["conscientiousness"]:
                                for extraversion in attribute_dict["extraversion"]:
                                    for agreeableness in attribute_dict["agreeableness"]:
                                        for neuroticism in attribute_dict["neuroticism"]:
                                            for residence in attribute_dict["residence"]:
                                                
                                                health_prob = random.random()
                                                if health_prob < 0.7:
                                                    health = "healthy"
                                                elif health_prob < 0.9:
                                                    health = "minor_issue"
                                                else:
                                                    health = "disabled"
                    
                                                for hobby in attribute_dict["hobby"]:
                                                    
                                                    if (profession == "student" or profession == "driver" or profession == "cleaner") and income_level == "high_income":
                                                        continue
                                                    
                                                    if profession =="farmer" and residence == "urban":
                                                        continue
                            
                                                    attribute_group_item = {
                                                        "age": age,
                                                        "gender": gender,
                                                        "income_level": income_level,
                                                        "profession": profession,
                                                        "openness": openness,
                                                        "conscientiousness": conscientiousness,
                                                        "extraversion": extraversion,
                                                        "agreeableness": agreeableness,
                                                        "neuroticism": neuroticism,
                                                        "residence": residence,
                                                        "health": health,
                                                        "hobby": hobby
                                                    }
                                                    attribute_groups.append(attribute_group_item)

        else:
            for gender in attribute_dict["gender"]:
                
                for profession in attribute_dict["profession"]:
                    if profession == "retiree" or profession == "student":
                        continue
            
                    for income_level in attribute_dict["income_level"]:
                        for openness in attribute_dict["openness"]:
                            for conscientiousness in attribute_dict["conscientiousness"]:
                                for extraversion in attribute_dict["extraversion"]:
                                    for agreeableness in attribute_dict["agreeableness"]:
                                        for neuroticism in attribute_dict["neuroticism"]:
                                            for residence in attribute_dict["residence"]:
                                                
                                                health_prob = random.random()
                                                if health_prob < 0.7:
                                                    health = "healthy"
                                                elif health_prob < 0.9:
                                                    health = "minor_issue"
                                                else:
                                                    health = "disabled"
                    
                                                for hobby in attribute_dict["hobby"]:
                                                    
                                                    
                                                    if (profession == "student" or profession == "driver" or profession == "cleaner") and income_level == "high_income":
                                                        continue
                                                    
                                                    if profession =="farmer" and residence == "urban":
                                                        continue
                                                    
                                                    attribute_group_item = {
                                                        "age": age,
                                                        "gender": gender,
                                                        "income_level": income_level,
                                                        "profession": profession,
                                                        "openness": openness,
                                                        "conscientiousness": conscientiousness,
                                                        "extraversion": extraversion,
                                                        "agreeableness": agreeableness,
                                                        "neuroticism": neuroticism,
                                                        "residence": residence,
                                                        "health": health,
                                                        "hobby": hobby
                                                    }
                                                    attribute_groups.append(attribute_group_item)
        
    return attribute_groups

if __name__ == '__main__':
    import json
    import random
    output_random_attribute_group = "random_attribute_group.jsonl"
    attr_group = get_proper_attribue_group() #413568
    random.shuffle(attr_group)
    print(len(attr_group))
    with open(output_random_attribute_group, "w", encoding='utf-8') as outfile:
        for item in attr_group[:20000]:
            json.dump(item, outfile, ensure_ascii=False)
            outfile.write("\n")