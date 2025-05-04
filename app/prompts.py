class Prompts:

    @staticmethod
    def get_prompt_v1(transcript):
        prompt = f"""
        You are a clinical documentation specialist AI. Your task is to extract relevant clinical information from a conversation transcript between a patient and a healthcare provider and write a comprehensive and structured SOAP (Subjective, Objective, Assessment, Plan) note.
        
        The transcript will contain back-and-forth dialogues. Assume one of the Speaker is a Doctor and the other is a Patient. Your goal is to **identify the key clinical information** using logical reasoning, and structure it into the SOAP format.
        
        ---
        Follow this chain of thought:
        1. First, **identify the main complaint or condition** being discussed.
        2. Extract and paraphrase the **subjective information** shared by the patient – including symptoms, severity, duration, lifestyle, past medical history, medications, and social factors.
        3. Extract the **objective findings** mentioned by the doctor – this may include vitals, physical exams, diagnostic tests, and lab results.
        4. Based on both subjective and objective data, **form a clinical assessment** – including possible diagnoses, their likelihood, and reasoning.
        5. Propose a **treatment or care plan** that aligns with the doctor’s advice and patient needs.
        
        Your output should be concise, medically coherent, and use clear clinical language. Do not copy verbatim from the transcript.
        
        ---
        Here are a few example transcripts and the corresponding SOAP notes:
        
        Example 1:
        
        Transcript:
        Doctor: What brings you in today?
        Patient: I've had a sore throat and fever for the last 3 days. It’s hard to swallow.
        Doctor: Have you had any cough or runny nose?
        Patient: Not really, just the sore throat and a mild headache.
        Doctor: Your throat looks red and inflamed. I’ll do a rapid strep test.
        
        SOAP:
        S: Patient reports sore throat, fever, and difficulty swallowing for 3 days. Also reports mild headache, no cough or nasal symptoms.
        O: Throat appears red and inflamed on examination. Rapid strep test ordered.
        A: Suspected streptococcal pharyngitis.
        P: Start antibiotics if rapid strep is positive. Recommend rest, hydration, and analgesics like acetaminophen for symptom relief.
        
        ---
        
        Example 2:
        
        Transcript:
        Doctor: How have your sugar levels been?
        Patient: Quite high. My fasting glucose this week was 160 mg/dL.
        Doctor: Any changes to your diet or medication?
        Patient: I’ve been skipping my morning insulin dose sometimes.
        
        SOAP:
        S: Patient reports elevated fasting glucose readings (160 mg/dL). Admits to occasionally skipping morning insulin dose.
        O: Self-reported blood glucose levels. No new labs done today.
        A: Poor glycemic control likely due to medication non-adherence.
        P: Reinforce importance of insulin adherence. Consider diabetes educator referral. Schedule follow-up in 1 week.
        
        ---
        
        Now, using the same format and reasoning, generate a SOAP note for the following transcript:
        
        [Insert Transcript Here]

        transcripts : <{transcript}>

        """
        return prompt