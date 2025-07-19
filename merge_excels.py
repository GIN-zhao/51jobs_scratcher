import pandas as pd
import os
import glob

def merge_excel_files(input_folder, output_filename):
    """
    合并指定文件夹下所有Excel文件，并进行数据清洗。

    :param input_folder: 存放Excel文件的文件夹路径。
    :param output_filename: 合并后输出的Excel文件名。
    """
    # 构建搜索路径，匹配所有.xlsx文件
    search_path = os.path.join(input_folder, '*.xlsx')
    excel_files = glob.glob(search_path)

    if not excel_files:
        print(f"在文件夹 '{input_folder}' 中没有找到任何Excel文件。")
        return

    print(f"找到以下文件进行合并: {excel_files}")

    # 读取所有Excel文件并合并到一个DataFrame中
    all_data_frames = [pd.read_excel(file) for file in excel_files]
    merged_df = pd.concat(all_data_frames, ignore_index=True)

    print(f"合并前总行数: {len(merged_df)}")

    # 1. 基于'URL'列去除重复行
    # 假设URL列的名称为'URL'，如果不是，需要修改这里的列名
    if 'URL' in merged_df.columns:
        # 先对URL列进行strip处理，去除前后空格
        if merged_df['URL'].dtype == 'object':
            print("对'URL'列进行strip处理...")
            merged_df['URL'] = merged_df['URL'].str.strip()
            
        cleaned_df = merged_df.drop_duplicates(subset=['URL'])
        print(f"基于URL去重后行数: {len(cleaned_df)}")
    else:
        print("警告: 未找到'URL'列，跳过基于URL的去重。")
        cleaned_df = merged_df.drop_duplicates()
        print(f"进行全局去重后行数: {len(cleaned_df)}")


    # 2. 去除第四列内容为空的行
    fourth_col_name_for_drop = cleaned_df.columns[3]
    cleaned_df = cleaned_df.dropna(subset=[fourth_col_name_for_drop])
    print(f"去除第四列为空的行后行数: {len(cleaned_df)}")

    # 3. 去除第四列中包含'https://'的行
    fourth_col_name_for_filter = cleaned_df.columns[3] 
    print(f"将对第四列 '{fourth_col_name_for_filter}' 进行筛选...")
    if cleaned_df[fourth_col_name_for_filter].dtype == 'object':
        cleaned_df = cleaned_df[~cleaned_df[fourth_col_name_for_filter].str.contains("https://", na=False)]
    print(f"筛选第四列后行数: {len(cleaned_df)}")

    # 保存结果到新的Excel文件
    try:
        cleaned_df.to_excel(output_filename, index=False, engine='openpyxl')
        print(f"成功合并 {len(excel_files)} 个文件，并保存到 '{output_filename}'")
        print(f"最终文件包含 {len(cleaned_df)} 行数据。")
    except Exception as e:
        print(f"保存文件时出错: {e}")

if __name__ == '__main__':
    # 设置输入文件夹和输出文件名
    INPUT_FOLDER = 'crawl_data'
    OUTPUT_FILE = 'merged_招聘分析结果.xlsx'
    
    # 执行合并功能
    merge_excel_files(INPUT_FOLDER, OUTPUT_FILE)
