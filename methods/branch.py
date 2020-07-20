from spiders import *

news_key = {
    'ctc': spider_ctc.CtcSpider,  # 中时电子报
    'vct': spider_vct.VctSpider,  # 汉声广播电台
    'tao': spider_tao.TaoSpider,  # 台湾关怀中国人权联盟&台湾人权促进会
    'tvct': spider_tvct.TvctSpider,  # TVBS新闻网& TVBS
    'pot': spider_pot.PotSpider,  # 基督长老教会
    'udn': spider_udn.UdnSpider,  # 联合新闻网
    'stm': spider_stm.StmSpider,  # 风传媒
    'tac': spider_tac.TacSpider,  # 苹果日报
    'pts': spider_pts.PtsSpider,  # 公视
    'nent': spider_nent.NentSpider,  # 东升电视台
    'nlct': spider_nlct.NlctSpider,  # 自由时报
    'tfot': spider_tfot.TfotSpider,  # 台湾民主基金会
    'cct': spider_cct.CctSpider,  # 华视
    'ect': spider_ect.EctSpider,  # 大纪元时报台湾版
    'sec': spider_sec.SecSpider,  # 三立电视
    'ttct': spider_ttct.TtctSpider,  # 台视
    'ogilvy': spider_ogilvy.OgilvySpider,  # 奥美公共关系顾问股份有限公司
    'jetgo': spider_jetgo.JetgoSpider,  # 战国策传播集团
    'fsr': spider_fsr.FsrSpider,  # 民视
    'realsurvey': spider_realsurvey.RealsurveySpider,  # 全国公信力民意调查
    'rti': spider_rti.RtiSpider,  # 中央广播电台(RTI)
    'bcc': spider_bcc.BccSpider,  # 中国广播公司

    'mpp': spider_mpp.MppSpider,  # 民众日报（台）2
    'merit': spider_merit.MeritSpider,  # 人间福报（台）2
    'dphk': spider_dphk.DphkSpider,  # 民主党(港) 2
    'hku': spider_hku.HkuSpider,  # 香港大学电子邮件服务器（港）2
    'kantei': spider_kantei.KanteiSpider,  # 首相官邸(日) 2
    'mofa': spider_mofa.MofaSpider,  # 外务省(日) 2
    'kr': spider_kr.KrSpider,  # 青瓦台(韩)2
    'mjoo': spider_mjoo.MjooSpider,  # 共同民主党（韩）1
    'tjp': spider_tjp.TjpSpider,  # 雅加达邮报(印) 2
    'rci': spider_rci.RciSpider,  # 印尼《共和国报》(印) 2
    'ttxvn': spider_ttxvn.TtxvnSpider,  # 越南通讯社(越) 2
    'dsc': spider_dsc.DscSpider,  # 越共电子报(越) 2

}


def branch(**kw):
    try:
        kw_news_key = kw.get('news_key')
        task_msg = kw.get('task_msg')
        method = kw.get('method')
        proxy = kw.get('proxy')
        req_params = {
            "task_msg": task_msg,
            "proxy": proxy,
            "method": method,
        }
        if method == 'news':
            pass
        elif method == 'search':
            req_params['keyword'] = kw.get('keyword')
        elif method == 'reg':
            req_params = kw
    except Exception:
        print('branch params errors')
    else:
        spider_run = news_key[kw_news_key](req_params)
        spider_run.crawling()
