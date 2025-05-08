import os

import dotenv
from google import genai

dotenv.load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = "Extract all text from the attached PDF using OCR and output the results in a well-structured Markdown (.md) format. Preserve the original formatting as much as possible. Do not include any additional explanations, comments, or modifications beyond the extracted content."


def get_ocr_text(file_path, prompt=prompt):
    sample_pdf = client.files.upload(file=file_path)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            prompt,
            sample_pdf,
        ],
    )
    text = response.text
    if "```" in text:
        return text.split("```")[1][9:]
    return text


if __name__ == "__main__":
    markdown_sample = """
# Physician’s Progress Note  

**Patient Seen & Examined:** ☒ Yes ☐ No  **Relevant History Taken:** ☒ Yes ☐ No  

## Subjective  
Patient is an 80-year-old female with PMHx of poorly-controlled DM, CVA, CAD, dementia, multiple bone fractures  
secondary to fall, AFTT, HTN, Afib. She is admitted to Bellaken Gardens for rehab, management of ongoing medical  
condition, medication administration, and assistance with ADLs. Recent ER visit on 12/03/2024 for elevated glucose,  
found to have UTI.  

Patient’s glucose continues to be elevated with a wide range. Patient denies symptoms.  

### Review of Systems  
☒ No Pain   ☒ No Cough   ☒ No Appetite Loss   ☒ No Constipation   ☒ No Diarrhea  
☐ Headache   ☐ SOB   ☐ Nausea   ☐ Vomiting   ☐ Abdominal Pain   ☐ Diarrhea   ☐ Pain   ☐ Cough   ☐ Sore Throat  

**Weight changes reviewed:** ☒ Yes ☐ No   **Any new behavior issues reviewed:** ☒ Yes ☐ No  
**Nurse’s notes reviewed:** ☒ Yes ☐ No   **SS notes reviewed:** ☒ Yes ☐ No   **IDT reviewed:** ☒ Yes ☐ No  

## Exam  
**Vitals:**  
B/P: 99/58 mmHg   Pulse: 64 bpm   Temp: 97.9 °F   RR: 16 breaths/min  
O2: 98%   Weight: 75 lbs   BS: 151 mg/dL  

**HEENT:** ☒ PERLA   ☐ Other:  
**Chest:** ☒ CTAB   ☐ Wheezing   ☐ Ronchi   ☐ Any other sounds:  
**CVS:** ☒ S1   ☒ S2   ☒ Regular   ☐ Irregular   ☒ No murmurs   ☐ Other:  
**Abdomen:** ☒ Soft   ☒ Non-tender   ☐ Other:  
**Neuro:** Any changes ☐ Yes   ☒ No  
**Edema:** ☐ Yes   ☒ No  
**Skin Issues:**  
**Other:**  

### Labs  
- **HgA1C:**  
- **TSH:**  
- **H/H:**  
- **BUN/Cr:**  
- **Cholesterol:**  
- **Other:** ☒ No New Labs  

## Assessment & Plan  
**Telephone & Medication Orders Reviewed:** ☒ Yes ☐ No   **Labs Reviewed:** ☒ Yes ☐ No  
**If pt is on psych meds, benefits, risks and dose reduction reviewed:** ☒ Yes ☐ No  

### Diagnoses and Treatment Plan  
1. **Poorly controlled diabetes** – Continue to monitor for signs/symptoms of hyper/hypoglycemia  
   - Obtain pre-prandial and post-prandial glucose checks  
   - Fiasp Injection Solution 100 unit/mL 5 unit subcutaneously three times a day  
   - Toujeo SoloStar Subcutaneous Solution Pen-injector 300 unit/mL 10 unit subcutaneously in the morning  
   - Glucose Oral Gel 15 mg/33 gm  

2. **HTN, BP within range**  
   - Losartan 100 mg by mouth in the morning  
   - AmLODIPine 10 mg by mouth one time a day  
   - Coreg 12.5 mg by mouth two times a day  

3. **CAD, stable**  
   - Atorvastatin 40 mg by mouth at bedtime  
   - Aspirin 81 mg by mouth in the morning  

4. **Hyponatremia, stable**  
   - Sodium Chloride 1 g by mouth one time a day  

5. **Glaucoma, stable**  
   - Alphagan P Ophthalmic Solution 0.1 % instill 1 drop in both eyes two times a day  

6. **Insomnia, stable**  
   - Melatonin 3 mg by mouth at bedtime  

7. **Constipation risk**  
   - Continue bowel regimen  

8. **Deconditioning/debility**  
   - Continue supportive care, skin surveillance, and fall precautions  
   - PT 3 times a week for 30 days  

9. **FEN**  
   - CCHO/NAS diet, Mechanical Soft texture, Thin Liquid consistency  
   - Continue Supplements  
   - Monitor weights  

**Code Status:** ☒ POLST REVIEWED & SIGNED   ☐ REFERRED FOR POLST COMPLETION  

**Patient is high risk for:**  
☒ Falls   ☒ Wt. Changes   ☒ Behavior issues   ☒ ADL decline   ☒ DVT   ☒ Skin breakdown   ☒ Aspiration  

**Patient Capacity:**  
☐ Has the capacity to understand and make medical decisions  
☐ Needs assistance to make medical decisions  
☒ Does not have the capacity to understand and make medical decisions  

☒ Discussed with Patient/Family/Nurse:  
☒ Goals of care   ☐ Discharge Planning   ☐ Change in treatment   ☐ POLST  

☒ 50% of exam spent in counseling and/or coordination of care (**Total time spent: 30 minutes**)  

---  

**Physician Signature:**  

**Date:** 01/07/2025  

**Patient Name:** Li Rong Li  
**Attending Physician:** Hugo Altamirano, MD  
"""
    prompt = f"""
Extract all text from the attached PDF using OCR and give me the output in same structure as pdf in markdown format.
Preserve the original formatting as much as possible.
If the text is in new line you should use new line in markdown too.
Do not include any additional explanations, comments, or modifications beyond the extracted content.
check format again and fonts size should be same.
here is the sample format of markdown {markdown_sample} this is how you 
"""
    md_data = get_ocr_text("AccessControl.pdf")
    with open("text.md", "w") as fp:
        fp.write(md_data)
