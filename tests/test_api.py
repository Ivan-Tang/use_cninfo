"""api 模块纯函数测试(无网络)。"""

from cninfo.api import (
    adjunct_to_url,
    clean_title,
    epoch_ms_to_ann_date,
    guess_plate,
    is_kind_report_body,
    is_periodic_report_body,
    to_ts_code,
)


def test_clean_title_strips_em_tags():
    assert clean_title("<em>贵州茅台</em>2024年年度报告") == "贵州茅台2024年年度报告"
    assert clean_title("  spaced  ") == "spaced"
    assert clean_title(None) == ""


def test_epoch_ms_to_ann_date_uses_beijing():
    # 2024-04-12 00:00 UTC  →  2024-04-12 08:00 Beijing  → 20240412
    assert epoch_ms_to_ann_date(1712880000000) == "20240412"
    # 2024-04-11 23:00 UTC  →  2024-04-12 07:00 Beijing  → 20240412 (而非 20240411)
    assert epoch_ms_to_ann_date(1712876400000) == "20240412"


def test_adjunct_to_url():
    assert adjunct_to_url("finalpage/2024-04-12/123.PDF") == (
        "http://static.cninfo.com.cn/finalpage/2024-04-12/123.PDF"
    )
    assert adjunct_to_url("/finalpage/2024-04-12/123.PDF") == (
        "http://static.cninfo.com.cn/finalpage/2024-04-12/123.PDF"
    )


def test_to_ts_code():
    assert to_ts_code("301580", "sz") == "301580.SZ"
    assert to_ts_code("600519", "sh") == "600519.SH"
    assert to_ts_code("870132", "bj") == "870132.BJ"


def test_guess_plate():
    assert guess_plate("000001") == "sz"
    assert guess_plate("301580") == "sz"
    assert guess_plate("600519") == "sh"
    assert guess_plate("688981") == "sh"
    assert guess_plate("870132") == "bj"


def test_is_periodic_report_body_accepts_main():
    assert is_periodic_report_body("2024年年度报告")
    assert is_periodic_report_body("贵州茅台2024年年度报告")
    assert is_periodic_report_body("2024年第一季度报告")
    assert is_periodic_report_body("2024年半年度报告")
    assert is_periodic_report_body("2024年第三季度报告")


def test_accepts_short_nian_variant():
    """「2024年度报告」少一个「年」,四大行、招商银行都这么写。

    只认「2024年年度报告」会让工行/农行/招行的正文取不到。
    """
    assert is_periodic_report_body("工商银行2024年度报告")
    assert is_periodic_report_body("农业银行2024年度报告")
    assert is_periodic_report_body("招商银行股份有限公司2024年度报告")
    assert is_kind_report_body("工商银行2024年度报告", 2024, "annual")
    # 年份仍要卡住
    assert not is_kind_report_body("工商银行2023年度报告", 2024, "annual")


def test_is_periodic_report_body_rejects_summary_and_audit():
    assert not is_periodic_report_body("2024年年度报告摘要")
    assert not is_periodic_report_body("2024年年度审计报告")
    assert not is_periodic_report_body("内部控制鉴证报告")
    assert not is_periodic_report_body("关于2024年年度报告披露的提示性公告")


def test_rejects_h_share_notice_variant():
    """A+H 公司另挂一份 H 股公告,标题也以「2024年年度报告」结尾。

    它比 A 股版晚发,按时间倒序翻页时排在前面,不排除就会把港式合并年报当正文。
    """
    assert not is_periodic_report_body("建设银行H股公告-2024年年度报告")
    assert not is_periodic_report_body("H股公告-2024年年度报告")
    assert not is_kind_report_body("建设银行H股公告-2024年年度报告", 2024, "annual")
    # A 股正文不受影响
    assert is_kind_report_body("建设银行2024年年度报告", 2024, "annual")
    assert is_kind_report_body("中国银行股份有限公司2024年年度报告", 2024, "annual")


def test_accepts_nianbao_baogao_typo():
    """紫金矿业把 FY2024 年报标题写成「2024年年报报告」（年报+报告）。

    是发行人笔误而非披露类型差异,但确实是正文 —— 不认它整份取不到。
    """
    assert is_periodic_report_body("紫金矿业集团股份有限公司2024年年报报告")
    assert is_kind_report_body("紫金矿业集团股份有限公司2024年年报报告", 2024, "annual")
    assert not is_kind_report_body("紫金矿业集团股份有限公司2023年年报报告", 2024, "annual")
    # 摘要仍要排掉
    assert not is_periodic_report_body("紫金矿业集团股份有限公司2024年年报报告摘要")


def test_is_kind_report_body_year_aware():
    assert is_kind_report_body("贵州茅台2024年年度报告", 2024, "annual")
    assert not is_kind_report_body("贵州茅台2023年年度报告", 2024, "annual")
    assert is_kind_report_body("某公司2024年第一季度报告", 2024, "q1")
    assert not is_kind_report_body("某公司2024年第三季度报告", 2024, "q1")
