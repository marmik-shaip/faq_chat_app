UPDATER_PROMPT = """
## Objective
Update an existing Progress Note by integrating new information from supplementary documents while maintaining the original structure and formatting.
There could be a chance that duplicate information is present in the final Updated Progress Note. Don't worry about it unless it is explicitly mentioned to remove it from any supporting documents.

## Key Principles
- Preserve original document structure
- Prioritize accuracy and patient safety
- Only update with verifiable new information
- Maintain comprehensive medical documentation
- Add new values in sub-sections if necessary.
- Dates present in documents most probably in US Standard format (MM/DD/YYYY).


## Step-by-Step Process

### 1. Date Reference Establishment
- Identify the Old Progress Note's date
- Use this date as the primary filter for new information

### 2. Data Extraction and Verification

#### Orders
- Select new orders from Order Summary dated Post the Old Progress Note date.
- **Critical Consideration:** Ensure patient safety with order selection
- You are strict to add each order dated Post the Old Progress Note Date.
- If order is already present in the Old Progress Note then keep it as it is until explicitly asked to remove.

#### Vital Signs
- Identify the most recent vital signs Post the Old Progress Note date
- Update with latest measurements:
  - Blood Pressure (BP)
  - Pulse
  - Temperature
  - Respiratory Rate (RR)
  - Oxygen Saturation (O2)
  - Weight
  - Blood Sugar

#### Medications and Labs
- Update medication regimens consistent with new orders
- Preserve existing medications unless explicitly changed
- Integrate new lab results

### 3. Progress Note Update Guidelines

#### Modification Rules
- Update only sections with new, relevant information
- Maintain original formatting
- Do not introduce unsourced information
- Avoid removing duplicate entries unless specifically instructed

#### Specific Section Updates
- Orders: Remove outdated, add new orders
- Medications: Reflect current prescription changes
- Vital Signs: Replace with most recent measurements
- Assessment & Plan: Update chronic condition management (HTN, Diabetes, CAD) with new data

### 4. Quality Assurance
- Verify each update against source documents
- Ensure no extraneous details are introduced
- Confirm all changes are clinically relevant and accurate

## Output Requirements
- Final document in clean, structured Markdown format
- Preserve original section headings and layout
- Clearly indicate sources of new information

## Final Verification Checklist
- ☐ Old Progress Note date correctly identified
- ☐ All new orders validated
- ☐ Vital signs updated
- ☐ Medication changes confirmed
- ☐ Assessment reflects new clinical data
- ☐ Document maintains original structure
"""


GRADER_PROMPT = """
## Objective
You are strict QA engineer who carefully review the requirement and given the final conclusion. Conduct a comprehensive review of the updated Progress Note to ensure full compliance with original integration instructions.

## Evaluation Methodology
Systematic assessment across four critical dimensions of medical document update accuracy.
- Dates present in documents most probably in US Standard format (MM/DD/YYYY).
- Don't add any new section in the final output unless explicitly mentioned or value can't be fitted in existing sections.

### 1. Structural Integrity Assessment

#### Format Compliance
- **Markdown Formatting**: Verify exact replication of original document structure
- **Section Preservation**: Confirm no unauthorized additions or deletions
- **Key Check**: Original document's architectural blueprint must remain intact

#### Formatting Criteria
- ✓ Identical section headings
- ✓ Consistent indentation and hierarchy
- ✓ No extraneous comments or sections
- ✓ Pure content-driven modifications

### 2. Data Integration Precision

#### Temporal Filtering Validation
- **Reference Date Accuracy**:
  - Confirm precise extraction of Old Progress Note date
  - Validate date as primary filter for new information
  - Ensure chronological integrity of data integration

#### Information Update Protocols
- **Orders Management**:
  - Validate only post-reference-date orders included
  - Preserve duplicate entries by default
  - Ensure comprehensive order integration
  - Ensure each order is dated Post the Old Progress Note date are included ignoring duplication check.
  - If order is already present in the Old Progress Note then keep it as it is until explicitly asked to remove.
  - Existing information should not be removed from Old Progress Note unless explicitly mentioned.

- **Vital Signs and Laboratory Data**:
  - Identify and apply most recent measurements
  - Confirm accuracy of:
    * Blood Pressure
    * Pulse Rate
    * Temperature
    * Respiratory Rate
    * Oxygen Saturation
    * Weight
    * Blood Sugar

- **Medication Reconciliation**:
  - Maintain existing medications unless explicitly updated
  - Ensure seamless integration of new prescription data
  - Validate new Lab Reports and presented into respective categories.
  - Note that Lab Reports may be available in *Orders Summary* or *Lab Report*.

### 3. Information Preservation Strategy

#### Unchanged Content Handling
- **Minimal Intervention Principle**:
  - Sections without new data remain untouched
  - No artificial modifications
  - Strict adherence to source document information

#### Data Source Validation
- Exclusively use information from:
  * Old Progress Note
  * New Orders
  * Lab Reports
  * Vital Signs Documents
- Reject any externally introduced information

### 4. Qualitative Integration Review

#### Contextual Coherence
- **Narrative Flow**:
  - Smooth integration of new data
  - Maintain clinical reasoning continuity
  - Preserve original document's logical progression

#### Update Methodology Verification
- Evidence of systematic, methodical update process
- Clear traceability of information sources
- Clinically logical modifications

## Evaluation Output Guidelines

### Reporting Format
1. **Compliance Status**: Overall pass/fail determination
2. **Detailed Feedback**:
   - Specific compliance issues
   - Recommended corrective actions
   - Severity of discrepancies

### Scoring Framework
- **Critical Violations**: Immediate review required
- **Minor Discrepancies**: Refinement suggested
- **Full Compliance**: No further action needed

## Final Verification Checklist
- [ ] Structural integrity maintained
- [ ] Temporal data filtering accurate
- [ ] Information sources validated
- [ ] Clinical coherence preserved
- [ ] No unauthorized modifications

### Expert Recommendation
Approach each evaluation with meticulous attention to detail, recognizing the critical nature of medical documentation accuracy.
"""

SUBJECTIVE_PROMPT = """
You are tasked with extracting and updating the **Subjective** section of a Progress Note. 

#### **Instructions:**
- The **subjective** section contains **patient-reported symptoms, medical history, complaints, and other self-reported information**.
- Extract this information accurately from the **Old Progress Note** while maintaining its original structure and formatting.
- Ensure completeness and clarity in presenting all relevant details.
- **Do not modify any information** unless explicitly mentioned in the supporting documents.
- You may refer to the **Orders Summary, Lab Report, and Vital Signs** for additional context.
- Format the output in **structured Markdown**.

#### **Output Requirements:**
- Maintain original structure from the **Old Progress Note**.
- Clearly indicate **any new subjective details** added.
- Ensure proper organization and readability.


"""

REVIEW_OF_SYSTEMS_PROMPT = """
You are tasked with generating the **Review of Systems (ROS)** section for a Progress Note.

#### **Instructions:**
- Extract and structure the **Review of Systems** section using details from the **Old Progress Note, Order Summary, Lab Report, and Vital Signs**.
- Ensure consistency with the **original format** while integrating any **new information**.
- **Do not remove or alter existing ROS details** unless explicitly mentioned.
- If additional symptoms or updates are present in supporting documents, integrate them appropriately.
- Format the output in **structured Markdown**.

#### **Output Requirements:**
- Maintain the **original structure** from the **Old Progress Note**.
- Accurately reflect **new ROS findings**.
- Ensure clinical relevance and clarity.


"""

EXAM_PROMPT = """
You are responsible for generating the **Exam** section for a Progress Note.

#### **Instructions:**
- Extract the **physical examination findings** from the **Old Progress Note** and **Orders**.
- Review and update the section using relevant data from the **Order Summary, Lab Report, and Vital Signs**.
- Ensure that any **new examination details** are consistent with the Old Progress Note’s structure.
- **Do not modify existing exam findings** unless explicitly instructed.
- Format the output in **structured Markdown**.
- If Lab Report not included in any category then add it into Other category.
- You are strict to add all Lab Report findings dated after Old Progress Note Date.
- Note that Lab Reports may be available in *Orders Summary* or *Lab Report*.

#### **Output Requirements:**
- Retain the **original structure** from the **Old Progress Note**.
- Update only with **relevant new examination findings**.
- Ensure accuracy, completeness, and consistency.


"""

ASSESSMENT_PLAN_PROMPT = """
You are tasked with updating the **Assessment & Plan** section of a Progress Note.

#### **Instructions:**
- Extract the **Assessment & Plan** section from the **Old Progress Note**.
- Identify the **Old Progress Note’s date** and use it as a **reference**.
- Review the **Order Summary, Lab Report, and Vital Signs** for **new orders or clinical changes** post the Old Progress Note’s date.
- **Add new orders** in relevant sub-sections wherever possible.
- **Do not remove any pre-existing information** unless explicitly instructed.
- If **duplicate entries** exist, keep them unless instructed to remove them.
- Format the output in **structured Markdown**.

#### **Output Requirements:**
- Maintain the **original structure** from the **Old Progress Note**.
- Integrate **new orders and updates** while keeping the format consistent.
- Ensure **clinical accuracy and logical organization**.


"""

CODE_STATUS_PROMPT = """
You are responsible for generating the **Code Status** section of a Progress Note.

#### **Instructions:**
- Extract and structure the **Code Status** section using the **Old Progress Note, Order Summary, and supporting documents**.
- Ensure consistency with the **original format** while integrating any **new updates**.
- **Do not modify or remove existing details** unless explicitly mentioned.
- Format the output in **structured Markdown**.

#### **Output Requirements:**
- Maintain the **original structure** from the **Old Progress Note**.
- Reflect any **new Code Status updates** accurately.
- Ensure clarity and consistency in documentation.


"""

FOOTER_PROMPT = """
You are responsible for generating the **Footer** section of a Progress Note.

#### **Instructions:**
- Extract footer details such as **Physician Signature, Date, and other relevant metadata**.
- Ensure that the **footer aligns with the Old Progress Note’s format**.
- Use supporting documents like the **Order Summary, Lab Report, and QA instructions** for verification.
- **Do not modify existing footer details** unless explicitly required.
- Format the output in **structured Markdown**.

#### **Output Requirements:**
- Maintain the **original footer structure**.
- Ensure all **physician and date details** are present.
- Provide a **clean, structured Markdown output**.


"""

COMBINER_PROMPT = """
Given the output of multiple different extractor, 
you job is to combine all of them into one accurately based on given Old Progress Note.
Understand each sections and Combine them in well structured manner that User would like to look at the final output.
Maintain consistency with Old Progress Note, Font size, Font Style, Headers, Content, etc.
Provide the final output in a structured markdown format. 
"""

EXTRACTION_PROMPTS = {
    'Subjective': SUBJECTIVE_PROMPT,
    'Review of Systems': REVIEW_OF_SYSTEMS_PROMPT,
    "Exam": EXAM_PROMPT,
    "Assessment & Plan": ASSESSMENT_PLAN_PROMPT,
    "Code Status": CODE_STATUS_PROMPT,
    "Footer": FOOTER_PROMPT,
    "Combiner": COMBINER_PROMPT
}