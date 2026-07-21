window.FIELD_SECTIONS = [
  {
    id: 'overview',
    title: '1. Tổng quan dự án',
    fields: [
      ['Tên dự án', 'project_name'],
      ['Mã dự án', 'curated_id'],
      ['Trạng thái dữ liệu', 'score_grade'],
      ['Ngày báo cáo mới nhất', 'latest_report_date'],
      ['Ngày báo cáo đầu tiên', 'first_report_date'],
      ['Số tin đã gom', 'mention_count'],
      ['Người gửi / nguồn nội bộ', 'senders'],
      ['Nguồn file/chat', 'source_files'],
      ['Ghi chú score', 'score_notes']
    ]
  },
  {
    id: 'location',
    title: '2. Vị trí & bản đồ',
    fields: [
      ['Vị trí / địa chỉ', 'location'],
      ['Tỉnh / Thành', 'province_city'],
      ['Quận / Khu vực', 'district_area'],
      ['Tọa độ', 'coordinates'],
      ['Chất lượng tọa độ', 'coordinate_quality'],
      ['Cảnh báo tọa độ', 'coordinate_anomaly_note'],
      ['Google Maps / My Maps', 'map_urls']
    ]
  },
  {
    id: 'scale',
    title: '3. Quy mô đất & sản phẩm',
    fields: [
      ['Diện tích đất chính', 'land_area_main'],
      ['Raw diện tích đất chính', 'land_area_main_raw'],
      ['Diện tích khác trong tin', 'other_area_mentions'],
      ['Loại dự án', 'project_type'],
      ['Cơ cấu sản phẩm theo phương án', 'product_structure'],
      ['Loại đất / mục đích sử dụng đất', 'land_type']
    ]
  },
  {
    id: 'planning',
    title: '4. Quy hoạch',
    fields: [
      ['Hồ sơ QH / 1/500 / 1/2000', 'planning_doc_status'],
      ['Tóm tắt quy hoạch', 'planning_summary'],
      ['Tầng cao', 'max_floors_clean'],
      ['FAR / HSSDĐ', 'far_clean'],
      ['Mật độ xây dựng', 'density_clean'],
      ['Dân số', 'population_clean']
    ]
  },
  {
    id: 'legal',
    title: '5. Pháp lý dự án',
    fields: [
      ['Tóm tắt pháp lý', 'legal_summary'],
      ['Trạng thái pháp lý', 'legal_status'],
      ['GPMB', 'gpm_status'],
      ['LUR / TSDĐ / nghĩa vụ tài chính', 'lur_status'],
      ['Phê duyệt / giao đất / GCN / đấu giá', 'approval_status']
    ]
  },
  {
    id: 'financial',
    title: '6. Giá, chi phí & hiệu quả',
    fields: [
      ['Giá chào / giá mua dự án', 'asking_land_price'],
      ['Giá bán sản phẩm', 'selling_price'],
      ['Chi phí đất / TSDĐ / LUR', 'land_cost'],
      ['Tổng mức đầu tư', 'total_investment_clean'],
      ['Doanh thu', 'revenue_clean'],
      ['Lợi nhuận', 'profit_clean'],
      ['IRR', 'irr_clean'],
      ['NPV', 'npv_clean'],
      ['Hoàn vốn', 'payback_clean'],
      ['Raw số liệu tài chính', 'financial_raw_mentions']
    ]
  },
  {
    id: 'risk',
    title: '7. Rủi ro & bước tiếp theo',
    fields: [
      ['Rủi ro / lưu ý', 'risks'],
      ['Next actions', 'next_actions'],
      ['Attachments', 'attachments'],
      ['Merged from IDs', 'merged_from_ids']
    ]
  },
  {
    id: 'score',
    title: '8. Chấm điểm dữ liệu',
    fields: [
      ['Tổng điểm', 'score_total'],
      ['Grade', 'score_grade'],
      ['Điểm vị trí', 'score_location'],
      ['Điểm dữ liệu', 'score_data'],
      ['Điểm quy hoạch', 'score_planning'],
      ['Điểm pháp lý', 'score_legal'],
      ['Điểm tài chính', 'score_financial'],
      ['Điểm trừ rủi ro', 'score_risk_penalty']
    ]
  }
];
