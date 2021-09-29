from string import uppercase
from operator import itemgetter

def vigenere_decrypt(target_freqs, input):
    nchars = len(uppercase)
    ordA = ord('A')
    sorted_targets = sorted(target_freqs)

    def frequency(input):
        result = [[c, 0.0] for c in uppercase]
        for c in input:
            result[c - ordA][1] += 1
        return result

    def correlation(input):
        result = 0.0
        freq = frequency(input)
        freq.sort(key=itemgetter(1))

        for i, f in enumerate(freq):
            result += f[1] * sorted_targets[i]
        return result

    cleaned = [ord(c) for c in input.upper() if c.isupper()]
    best_len = 0
    best_corr = -100.0

    # Assume that if there are less than 20 characters
    # per column, the key's too long to guess
    for i in xrange(2, len(cleaned) // 20):
        pieces = [[] for _ in xrange(i)]
        for j, c in enumerate(cleaned):
            pieces[j % i].append(c)

        # The correlation seems to increase for smaller
        # pieces/longer keys, so weigh against them a little
        corr = -0.5 * i + sum(correlation(p) for p in pieces)

        if corr > best_corr:
            best_len = i
            best_corr = corr

    if best_len == 0:
        return ("Text is too short to analyze", "")

    pieces = [[] for _ in xrange(best_len)]
    for i, c in enumerate(cleaned):
        pieces[i % best_len].append(c)

    freqs = [frequency(p) for p in pieces]

    key = ""
    for fr in freqs:
        fr.sort(key=itemgetter(1), reverse=True)

        m = 0
        max_corr = 0.0
        for j in xrange(nchars):
            corr = 0.0
            c = ordA + j
            for frc in fr:
                d = (ord(frc[0]) - c + nchars) % nchars
                corr += frc[1] * target_freqs[d]

            if corr > max_corr:
                m = j
                max_corr = corr

        key += chr(m + ordA)

    r = (chr((c - ord(key[i % best_len]) + nchars) % nchars + ordA)
         for i, c in enumerate(cleaned))
    return (key, "".join(r))


def main():
    encoded = """
    Yse lncsz bplr-izcarpnzjo dkxnroueius zf g uzlefwpnfmeznn cousex bls ltcmaqltki my Rjzn Hfetoxea Gqmexyt axtfnj 1467 fyd axpd g rptgq nivmpr jndc zt dwoynh hjewkjy cousex fwpnfmezx. Llhjcto'x dyyypm uswy ybttimpd gqahggpty fqtkw debjcar bzrjx, lnj xhizhsey bprk nydohltki my cwttosr tnj wezypr uk ehk hzrxjdpusoitl llvmlbky tn zmp cousexypxz. Qltkw, tn 1508, Ptsatsps Zwttnjxiax, tn nnd wuwv Puqtgxfahof, tnbjytki ehk ylbaql rkhea, g hciznnar hzmvtyety zf zmp Volpnkwp cousex. Yse Zwttnjxiax nivmpr, nthebjc, otqj pxtgijjo a vwzgxjdsoap, roltd, gso pxjoiiylbrj dyyypm ltc scnecnnyg hjewkjy cousex fwpnfmezx.

Hhgy ts tth ktthn gx ehk Atgksprk htpnjc wgx zroltngqwy jjdcxnmej gj Gotgat Gltzndtg Gplrfdo os siy 1553 gzoq Ql cokca jjw. Sol. Riualn Hfetoxea Hjwlgxz. Hk gfiry fpus ehk ylbaql rkhea uk Eroysesnfs, hze ajipd g wppkfeitl "noaseexxtgt" (f vee) yz scnecn htpnjc arusahjes kapre qptzjc. Wnjcegx Llhjcto fyd Zwttnjxiax fski l focpd vfetkwy ol xfbyyttaytotx, Merqlsu'x dcnjxe sjlnz yse vfetkwy ol xfbyyttaytotx noaqo bk jlsoqj cnfygki disuwy hd derjntosr a tjh kkd. Veex hexj eyvnnarqj sosrlk bzrjx zr ymzrz usrgxps, qszwt yz buys pgweikx tn gigathp, ox ycatxxizypd "uze ol glnj" fwotl hizm ehk rpsyfre. Hjwlgxz's sjehui ehax cewztrki dtxtyg yjnuxney ltc otqj tnj vee. Fd iz nd rkqltoaple jlse yz skhfrk f dhuwe kkd ahxfde, yfj be f arkatoax aroaltk hznbjcsgytot, Gplrfdo'y xjszjx wgx notxtdkwlbrd xoxj deizce.

Hqliyj oe Bnretjce vzmloxsej mts jjdcxnatoty ol f disnwax gft yycotlpr gzeoqjj cousex gpfuwp tnj noawe ol Mpnxd TIO tq Fxfyck, ny 1586. Lgypr, os ehk 19ys ckseuxd, ehk nyvkseius zf Hjwlgxz's inahkw hay rtsgyerogftki eo Bnretjce. Jfgij Plht ny hox moup Ehk Hzdkgcegppry qlmkseej yse sndazycihzeius my yfjitl ehgy siyyzre mld "olyoxjo tnnd isuzrzfyt itytxnmuznzn gso itxeegi yasjo a xjrrkxdibj lnj jwesjytgwj cousex kzr nnx [Volpnkwp] tntfgn mp hgi yozmtnm yz du bttn ne". pohzCZK{g1gt3w3_n1pn3wd_ax3s7_maj_5352gq72}

Tnj Gimjyexj nivmpr mftnki l rkuftgytot kzr hjtnm jickueiusllrd dtxtyg. Tteej fftntc ati xazmpmgytcofy Cnfclkx Wuzbtdmj Oojldot (Qpwox Naxwzlr) hllrjo tnj Gimjyexj nivmpr asmrkfvahqp it mts 1868 vnpck "Yse Gqahggpt Inahkw" tn g hsiricet'x xamfkitj. Tn 1917, Yhtetytfoh Lmkwtcgs oeyhcihjo tnj Gimjyexj nivmpr gx "tmvtdsogwe uk ergsdlgytot". Ysiy wppayltoty wgx yoz ipskwgej. Hsaxqps Hfmbglp iy pyocs eo nfge hwzkks l vgwtaty zf zmp cousex fd egwwy gx 1854; socjgex, mp doiy't vzmloxs hox hoxp. Vayndko jytowple gcoqj ehk htpnjc ati auhqtsnjo tnj eeimyiwzp it yse 19zm netyfre. Jget gpfuwp tnnd, tntfgn, xzmk xvirqpd iwjpzfyarddty hzuri zcifdiusllrd mrkfv tnj nivmpr os ehk 16ys ckseuxd.

Nreueomwlpnnn srnoe xzwe axpd gx l cgqnurfeius lij gj tnj Dwoxd Axrj bkyheks 1914 lnj 1940.
Yse Bnretjce inahkw ts ynxprj pnuzrh zt me g kteri nivmpr ok tt ox fski tn ityjasntoty woys cousex itsqx. Ehk Hznljoexfee Yyltkx zf Grprohl, fuw pxgralk, zdej f mrgxd cousex itsq yz isuwesjyt zmp Volpnkwp cousex ifrosr tnj Lmkwtcgs Nibnw Wgw. Ehk Hznljoexfny'y rpsyfrey bprk klr lwzm yjnrky lnj yse Astot wpgaqlrrd nrghvej yseow xeyxlgkx. Ehxtfgntft zmp wgw, ehk Hznljoexfee rjldkwdhou arorlroqj rkqtej zaot ysrkj vee usrgxps, "Sfycnjdtkw Mlakq", "Curalkyp Voheoxd" lnj, fd tnj hax hlmk yz a iqzsk, "Hzmk Wptxnmuznzn".

Mnwbkwe Vkwyas yciki eo xjaaow ehk gcoqjy cousex (hcegytnm yse Bjcngr-Gimjyexj nivmpr os 1918), muz, sz mgyeex bsaz mp doi, ehk htpnjc wgx dtoqw vaqyexfmlk yz cxdatgsllexts. Bjcngr'd wuwv, hubpvkw, pvkseugqwy rjo tu yse usp-torp pgi, l tnjzrkytcgqwy asmrkfvahqp cousex.
"""

    english_frequences = [
        0.08167, 0.01492, 0.02782, 0.04253, 0.12702, 0.02228, 0.02015,
        0.06094, 0.06966, 0.00153, 0.00772, 0.04025, 0.02406, 0.06749,
        0.07507, 0.01929, 0.00095, 0.05987, 0.06327, 0.09056, 0.02758,
        0.00978, 0.02360, 0.00150, 0.01974, 0.00074]

    (key, decoded) = vigenere_decrypt(english_frequences, encoded.upper())
    print("Key:", key)
    print("\nText:", decoded)

    from pycipher import Vigenere
    plaintext = Vigenere('FLAG').decipher(encoded)
    print (plaintext)

main()

