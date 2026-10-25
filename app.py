import streamlit as st
import json
import os
from datetime import datetime

# ============================================================
# STUDENT ASSIGNMENT SUBMISSION INTEGRITY CHECKER
# CRC-based file/data integrity verification
# ============================================================

st.set_page_config(
    page_title="Assignment Integrity Checker",
    page_icon="🔐",
    layout="wide"
)

RECORD_FILE = "crc_records.json"

# CRC configurations: width, polynomial, initial value
CRC_CONFIG = {
    "CRC-3": {"width": 3, "polynomial": 0b011, "initial": 0},
    "CRC-4": {"width": 4, "polynomial": 0b0011, "initial": 0},
    "CRC-8": {"width": 8, "polynomial": 0x07, "initial": 0},
}

# -------------------- Styling --------------------
st.markdown("""
<style>
.main-title {
    font-size: 38px;
    font-weight: 800;
    margin-bottom: 4px;
}

.subtitle {
    color: #667085;
    font-size: 17px;
    margin-bottom: 25px;
}

.card {
    padding: 18px;
    border: 1px solid #e4e7ec;
    border-radius: 12px;
    background: #ffffff;
}

.result {
    padding: 18px;
    border-radius: 12px;
    margin-top: 10px;
}

.small {
    color: #667085;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# -------------------- Storage --------------------
def load_records():
    if not os.path.exists(RECORD_FILE):
        return []

    try:
        with open(RECORD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_records(records):
    with open(RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4)


# -------------------- Delete Record --------------------
def delete_record(record_id):
    records = load_records()

    updated_records = [
        record for record in records
        if record["id"] != record_id
    ]

    save_records(updated_records)


# -------------------- CRC Core --------------------
def calculate_crc(bits, width, polynomial, initial=0):
    """
    Manual modulo-2 CRC calculation using XOR.
    bits: string containing only 0 and 1
    returns CRC remainder as a binary string
    """

    if not bits or any(bit not in "01" for bit in bits):
        raise ValueError("CRC input must contain only 0 and 1.")

    data = [int(bit) for bit in bits]
    register = initial

    for bit in data:
        top_bit = (register >> (width - 1)) & 1
        register = ((register << 1) | bit) & ((1 << width) - 1)

        if top_bit:
            register ^= polynomial

    return format(register, f"0{width}b")


def bytes_to_bits(data):
    return "".join(format(byte, "08b") for byte in data)


def text_to_bits(text):
    return bytes_to_bits(text.encode("utf-8"))


def calculate_for_data(data_bytes, algorithm):
    cfg = CRC_CONFIG[algorithm]

    bits = bytes_to_bits(data_bytes)

    crc = calculate_crc(
        bits,
        cfg["width"],
        cfg["polynomial"],
        cfg["initial"]
    )

    return crc, bits


def calculate_for_binary(binary_text, algorithm):
    cfg = CRC_CONFIG[algorithm]

    crc = calculate_crc(
        binary_text,
        cfg["width"],
        cfg["polynomial"],
        cfg["initial"]
    )

    return crc


def flip_bit(bits, position):
    if not bits:
        return bits

    if position < 0 or position >= len(bits):
        return bits

    changed = list(bits)

    changed[position] = (
        "1" if changed[position] == "0" else "0"
    )

    return "".join(changed)


# -------------------- UI Header --------------------
st.markdown(
    '<div class="main-title">'
    '🔐 Student Assignment Submission Integrity Checker'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'CRC-based detection of accidental modification or corruption '
    'of assignment data and files.'
    '</div>',
    unsafe_allow_html=True
)


# -------------------- Sidebar --------------------
st.sidebar.header("⚙️ CRC Configuration")

algorithm = st.sidebar.selectbox(
    "Select CRC Algorithm",
    list(CRC_CONFIG.keys()),
    index=2
)

cfg = CRC_CONFIG[algorithm]

st.sidebar.write(f"**Width:** {cfg['width']} bits")

st.sidebar.write(
    f"**Polynomial:** "
    f"{cfg['polynomial']:0{cfg['width']}b}"
)

st.sidebar.info(
    "For the live demonstration, explain one CRC algorithm in detail "
    "and briefly demonstrate the others."
)


# -------------------- Tabs --------------------
tab2, tab3 = st.tabs([
    "📁 File Submission",
    "🔎 Verify Submission"
])


# ============================================================
# TAB 2: FILE SUBMISSION
# ============================================================
with tab2:

    st.subheader("Submit an Assignment File")

    student_name = st.text_input(
        "Student Name",
        key="student_name"
    )

    roll_no = st.text_input(
        "Roll / Enrollment Number",
        key="roll_no"
    )

    uploaded_file = st.file_uploader(
        "Upload Assignment",
        type=None,
        key="assignment_upload"
    )

    if st.button(
        "Submit & Generate CRC",
        key="submit_file"
    ):

        if not student_name.strip():

            st.warning("Enter the student name.")

        elif not roll_no.strip():

            st.warning("Enter the roll/enrollment number.")

        elif uploaded_file is None:

            st.warning("Upload an assignment file.")

        else:

            file_bytes = uploaded_file.getvalue()

            crc, bits = calculate_for_data(
                file_bytes,
                algorithm
            )

            record = {
                "id": datetime.now().strftime(
                    "%Y%m%d%H%M%S%f"
                ),

                "student_name": student_name.strip(),

                "roll_no": roll_no.strip(),

                "file_name": uploaded_file.name,

                "file_size": len(file_bytes),

                "algorithm": algorithm,

                "crc": crc,

                "submitted_at": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }

            records = load_records()

            records.append(record)

            save_records(records)

            st.session_state["last_submission"] = record

            st.success(
                "Assignment submitted and CRC recorded."
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Student",
                record["student_name"]
            )

            c2.metric(
                "File Size",
                f"{record['file_size']} bytes"
            )

            c3.metric(
                "Algorithm",
                algorithm
            )

            c4.metric(
                "CRC",
                record["crc"]
            )

            st.info(
                "The CRC value is now the recorded "
                "integrity reference for this submission."
            )


# ============================================================
# TAB 3: VERIFY SUBMISSION
# ============================================================
with tab3:

    st.subheader("Verify a Previously Submitted Assignment")

    records = load_records()

    if not records:

        st.info(
            "No submissions found. Submit an assignment first."
        )

    else:

        # ----------------------------------------------------
        # Create submission labels
        # ----------------------------------------------------
        labels = [
            f"{r['roll_no']} | "
            f"{r['student_name']} | "
            f"{r['file_name']} | "
            f"{r['submitted_at']}"
            for r in records
        ]

        selected_index = st.selectbox(
            "Select a submission record",
            range(len(records)),
            format_func=lambda i: labels[i],
            key="selected_submission"
        )

        selected = records[selected_index]

        # ----------------------------------------------------
        # Original Submission Information
        # ----------------------------------------------------
        st.write("### Original Submission")

        c1, c2, c3, c4 = st.columns(4)

        c1.write(
            f"**Student:** {selected['student_name']}"
        )

        c2.write(
            f"**Roll No:** {selected['roll_no']}"
        )

        c3.write(
            f"**File:** {selected['file_name']}"
        )

        c4.write(
            f"**Stored CRC:** `{selected['crc']}`"
        )

        # ----------------------------------------------------
        # Verification File
        # ----------------------------------------------------
        verification_file = st.file_uploader(
            "Upload the file you want to verify",
            type=None,
            key=f"verify_{selected['id']}"
        )

        if st.button(
            "Verify File Integrity",
            key="verify_button"
        ):

            if verification_file is None:

                st.warning(
                    "Upload the file to verify."
                )

            else:

                current_bytes = verification_file.getvalue()

                current_crc, _ = calculate_for_data(
                    current_bytes,
                    selected["algorithm"]
                )

                st.write(
                    f"**Stored CRC:** `{selected['crc']}`"
                )

                st.write(
                    f"**Current CRC:** `{current_crc}`"
                )

                if current_crc == selected["crc"]:

                    st.success(
                        "✅ NO ERROR DETECTED — CRC values match. "
                        "The received file matches the recorded submission."
                    )

                else:

                    st.error(
                        "❌ ERROR DETECTED — CRC values do not match. "
                        "The received file is different from the recorded submission."
                    )

        # ====================================================
        # DELETE SUBMISSION
        # ====================================================

        st.divider()

        st.write("### 🗑️ Manage Submission")

        st.caption(
            "Remove an old submission record from the verification list."
        )

        if st.button(
            "🗑️ Delete Selected Submission",
            key="delete_submission"
        ):

            st.session_state["confirm_delete"] = True

        # ----------------------------------------------------
        # Confirmation
        # ----------------------------------------------------
        if st.session_state.get("confirm_delete", False):

            st.warning(
                f"Are you sure you want to delete the submission "
                f"for **{selected['student_name']}** "
                f"({selected['file_name']})?"
            )

            confirm_col1, confirm_col2 = st.columns(2)

            with confirm_col1:

                if st.button(
                    "✅ Yes, Delete",
                    key="confirm_delete_button"
                ):

                    delete_record(selected["id"])

                    st.session_state["confirm_delete"] = False

                    st.success(
                        "Submission record deleted successfully."
                    )

                    st.rerun()

            with confirm_col2:

                if st.button(
                    "❌ Cancel",
                    key="cancel_delete_button"
                ):

                    st.session_state["confirm_delete"] = False

                    st.rerun()


# -------------------- Footer --------------------
st.divider()

st.caption(
    "CRC detects data changes/corruption by comparing CRC results. "
    "It is an error-detection mechanism, not a cryptographic security guarantee."
)