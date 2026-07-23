# FS final 2026-07-23

Saved for Hòa Đại ka on 2026-07-23 after deployed FS Excel export fixes.

Files:
- `fs_final_2026-07-23.html` — copy of `public_final_2026_07_11/fs.html` at final state.
- `../outputs/FS_FULL_input_2026-07-23_native.xlsx` — exported workbook generated from the real input file during QA.

Validation summary:
- Fuzz comparator: PASS 25/25 before reverting IRR/NPV to native Excel functions per user preference.
- Final user-preference build uses native Excel functions:
  - `NPV` / `NPV bán riêng`: `XNPV(...)`
  - `IRR CĐT` / `IRR dự án`: `XIRR(...)`
- Real input QA (`C:/Users/HoaD-CVDT/Downloads/FS_INPUT_2026-07-23.xlsx`): PASS.
  - NPV diff ~ -0.00003 VND
  - IRReq diff ~ -4.62e-10
  - IRRprj diff ~ -3.93e-10
  - NPVsale diff = 0
  - LNTT/TNDN/LNST diffs only rounding noise.

Deployed URL:
- https://lhrealestate.web.app
