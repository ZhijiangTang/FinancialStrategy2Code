export OPENAI_API_KEY="sk-cjnnfcatihrikdywnbebqofrrhfyzmzoturkcyyagrnlrjud"

GPT_VERSION="Qwen/Qwen3-30B-A3B"

PAPER_NAME="Momentum"
PDF_LATEX_CLEANED_PATH="../strategies/Momentum.tex" # _cleaned.tex
OUTPUT_DIR="../outputs/Momentum"
OUTPUT_REPO_DIR="../outputs/Momentum_repo"

mkdir -p $OUTPUT_DIR
mkdir -p $OUTPUT_REPO_DIR

echo $PAPER_NAME

echo "------- PaperCoder -------"

python ../codes/1_planning.py \
    --paper_name $PAPER_NAME \
    --gpt_version ${GPT_VERSION} \
    --pdf_latex_path ${PDF_LATEX_CLEANED_PATH} \
    --paper_format LaTeX \
    --output_dir ${OUTPUT_DIR}


python ../codes/1.1_extract_config.py \
    --paper_name $PAPER_NAME \
    --output_dir ${OUTPUT_DIR}

cp -rp ${OUTPUT_DIR}/planning_config.yaml ${OUTPUT_REPO_DIR}/config.yaml

python ../codes/2_analyzing.py \
    --paper_name $PAPER_NAME \
    --gpt_version ${GPT_VERSION} \
    --pdf_latex_path ${PDF_LATEX_CLEANED_PATH} \
    --paper_format LaTeX \
    --output_dir ${OUTPUT_DIR}

python ../codes/3_coding.py  \
    --paper_name $PAPER_NAME \
    --gpt_version ${GPT_VERSION} \
    --pdf_latex_path ${PDF_LATEX_CLEANED_PATH} \
    --paper_format LaTeX \
    --output_dir ${OUTPUT_DIR} \
    --output_repo_dir ${OUTPUT_REPO_DIR} \