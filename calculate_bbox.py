import math
import pandas as pd

KM_PER_DEGREE_LAT = 111.132

def get_bounding_box(latitude, longitude, radius_km=5):
    """
    计算给定经纬度中心点和半径的矩形边界框。
    :param latitude: 中心点的纬度 (单位: 度)
    :param longitude: 中心点的经度 (单位: 度)
    :param radius_km: 半径 (单位: 公里)，默认为5公里
    :return: 一个包含四个值的元组 (min_lat, max_lat, min_lon, max_lon)
    """
    if not (-90 <= latitude <= 90):
        raise ValueError("纬度必须在 -90 到 90 度之间。")
    if not (-180 <= longitude <= 180):
        raise ValueError("经度必须在 -180 到 180 度之间。")

    lat_rad = math.radians(latitude)
    km_per_degree_lon = 111.320 * math.cos(lat_rad)

    lat_diff = radius_km / KM_PER_DEGREE_LAT
    
    if km_per_degree_lon > 0.001:
        lon_diff = radius_km / km_per_degree_lon
    else:
        lon_diff = 360

    min_lat = latitude - lat_diff
    max_lat = latitude + lat_diff
    min_lon = longitude - lon_diff
    max_lon = longitude + lon_diff

    return (min_lat, max_lat, min_lon, max_lon)

def is_within_bbox(latitude, longitude, bbox):
    """
    判断一个坐标点是否在给定的边界框内。
    :param latitude: 要检查的点的纬度
    :param longitude: 要检查的点的经度
    :param bbox: 一个包含(min_lat, max_lat, min_lon, max_lon)的元组
    :return: 如果点在边界框内，则返回 True，否则返回 False
    """
    min_lat, max_lat, min_lon, max_lon = bbox
    
    if not (min_lat <= latitude <= max_lat):
        return False
    if not (min_lon <= longitude <= max_lon):
        return False
    
    return True

if __name__ == "__main__":
    # --- 1. 定义一个中心区域 ---
    center_lat = 25.041056
    center_lon = 121.574383
    radius_km = 2
    
    # 计算这个中心区域的边界框
    target_bbox = get_bounding_box(center_lat, center_lon, radius_km)
    
    print("--- 目标区域已设定 ---")
    print(f"中心点: (纬度: {center_lat}, 经度: {center_lon})")
    print(f"半径: {radius_km} 公里")
    print(f"计算出的边界框: Lat({target_bbox[0]:.4f}, {target_bbox[1]:.4f}), Lon({target_bbox[2]:.4f}, {target_bbox[3]:.4f})")
    
    # --- 2. 读取CSV文件并逐个判断 ---
    csv_filename = 'img_info.csv'
    print(f"\n--- 正在从 '{csv_filename}' 读取坐标并进行判断 ---")
    cnt_valid = 0
    try:
        df = pd.read_csv(csv_filename, header=None)
        
        if df.shape[1] < 3:
            print(f"错误: CSV文件 '{csv_filename}' 的列数少于3，无法找到经纬度。")
        else:
            print(f"成功读取 {len(df)} 条记录。开始判断...")
            
            for index, row in df.iterrows():
                try:
                    # 第二列是纬度 (索引1)，第三列是经度 (索引2)
                    point_lat = float(row[2])
                    point_lon = float(row[1])
                    
                    # 调用函数进行判断
                    is_inside = is_within_bbox(point_lat, point_lon, target_bbox)
                    if is_inside:
                        cnt_valid += 1
                    
                except (ValueError, TypeError):
                    print(f"  - 记录 {index + 1}: 跳过 (无效的坐标数据)")
            print(f'--- 结果 ---\n有效记录数: {cnt_valid}')
    except FileNotFoundError:
        print(f"错误: 未找到文件 '{csv_filename}'。")
    except Exception as e:
        print(f"处理文件时发生错误: {e}")
