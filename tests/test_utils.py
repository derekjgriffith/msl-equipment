import enum
import datetime
from xml.etree.cElementTree import Element, Comment

import pytest

from msl.equipment.utils import (
    convert_to_enum,
    convert_to_primitive,
    convert_to_date,
    convert_to_xml_string,
    xml_comment,
    xml_element,
)


def test_convert_to_enum():

    class MyEnum(enum.Enum):
        ONE = 'value'
        XXX_TWO = 2
        three = 3.0
        F_O_U_R = 'f o U r'
        FiVe = -5+5j
        SIX = True
        BYTES = b'\x00\x01'

    assert convert_to_enum('unknown', MyEnum, strict=False) == 'unknown'
    assert convert_to_enum(99, MyEnum, strict=False) == 99
    assert convert_to_enum(8j, MyEnum, strict=False) == 8j
    assert convert_to_enum(7.2, MyEnum, strict=False) == 7.2

    assert convert_to_enum(MyEnum.ONE, MyEnum) == MyEnum.ONE
    assert convert_to_enum('value', MyEnum) == MyEnum.ONE
    assert convert_to_enum('ONE', MyEnum) == MyEnum.ONE
    assert convert_to_enum('ONE', MyEnum) == MyEnum.ONE
    assert convert_to_enum('ONE', MyEnum, prefix='O') == MyEnum.ONE
    assert convert_to_enum('ONE', MyEnum, prefix='ON') == MyEnum.ONE
    assert convert_to_enum('ONE', MyEnum, prefix='ONE') == MyEnum.ONE
    assert convert_to_enum('one', MyEnum, to_upper=True) == MyEnum.ONE
    with pytest.raises(ValueError):
        convert_to_enum('one', MyEnum)
    assert convert_to_enum('one', MyEnum, prefix='one', to_upper=True) == MyEnum.ONE

    assert convert_to_enum(MyEnum.XXX_TWO, MyEnum) == MyEnum.XXX_TWO
    assert convert_to_enum(2, MyEnum) == MyEnum.XXX_TWO
    assert convert_to_enum('XXX_TWO', MyEnum) == MyEnum.XXX_TWO
    assert convert_to_enum('XXX TWO', MyEnum) == MyEnum.XXX_TWO
    assert convert_to_enum('xXx_twO', MyEnum, to_upper=True) == MyEnum.XXX_TWO
    assert convert_to_enum('Xxx TwO', MyEnum, to_upper=True) == MyEnum.XXX_TWO
    assert convert_to_enum('two', MyEnum, prefix='xxx_', to_upper=True) == MyEnum.XXX_TWO
    with pytest.raises(ValueError):
        convert_to_enum('TWO', MyEnum, prefix='xxx')
    assert convert_to_enum('TWO', MyEnum, prefix='xx', strict=False) == 'TWO'
    assert convert_to_enum('TWO', MyEnum, prefix='XXX_') == MyEnum.XXX_TWO

    assert convert_to_enum(MyEnum.three, MyEnum) == MyEnum.three
    assert convert_to_enum(3, MyEnum) == MyEnum.three
    assert convert_to_enum(3.0, MyEnum) == MyEnum.three
    assert convert_to_enum('three', MyEnum) == MyEnum.three
    with pytest.raises(ValueError):
        convert_to_enum('three', MyEnum, to_upper=True)
    with pytest.raises(ValueError):
        convert_to_enum('THREE', MyEnum)

    assert convert_to_enum(MyEnum.F_O_U_R, MyEnum) == MyEnum.F_O_U_R
    assert convert_to_enum('F O U R', MyEnum) == MyEnum.F_O_U_R
    assert convert_to_enum('f o U r', MyEnum) == MyEnum.F_O_U_R
    assert convert_to_enum('f o u r', MyEnum, to_upper=True) == MyEnum.F_O_U_R
    with pytest.raises(ValueError):
        convert_to_enum('f o u r', MyEnum)
    assert convert_to_enum('F_O_U_R', MyEnum) == MyEnum.F_O_U_R

    assert convert_to_enum(MyEnum.FiVe, MyEnum) == MyEnum.FiVe
    assert convert_to_enum(-5+5j, MyEnum) == MyEnum.FiVe
    assert convert_to_enum('FiVe', MyEnum) == MyEnum.FiVe
    with pytest.raises(ValueError):
        assert convert_to_enum('FiVe', MyEnum, to_upper=True)
    with pytest.raises(ValueError):
        assert convert_to_enum('FiVe', MyEnum, prefix='FI')

    assert convert_to_enum(True, MyEnum) == MyEnum.SIX
    assert convert_to_enum(1, MyEnum) == MyEnum.SIX
    assert convert_to_enum('SIX', MyEnum) == MyEnum.SIX
    assert convert_to_enum('six', MyEnum, to_upper=True) == MyEnum.SIX
    assert convert_to_enum('six', MyEnum, prefix='six', to_upper=True) == MyEnum.SIX
    with pytest.raises(ValueError):
        convert_to_enum('six', MyEnum, prefix='Six', to_upper=True)
    convert_to_enum('Six', MyEnum, prefix='Si', to_upper=True)

    assert convert_to_enum(b'\x00\x01', MyEnum) == MyEnum.BYTES
    assert convert_to_enum('bytes', MyEnum, to_upper=True) == MyEnum.BYTES
    with pytest.raises(ValueError):
        convert_to_enum('bytes', MyEnum)


def test_string_to_bool_int_float_complex():
    assert convert_to_primitive('none') is None
    assert convert_to_primitive('None') is None
    assert convert_to_primitive('nOnE') is None
    assert convert_to_primitive('  None \t') is None
    assert convert_to_primitive(None) is None

    assert convert_to_primitive('true') is True
    assert convert_to_primitive('True') is True
    assert convert_to_primitive('TRuE') is True
    assert convert_to_primitive('  True\n') is True
    assert convert_to_primitive(True) is True
    assert convert_to_primitive('false') is False
    assert convert_to_primitive('False') is False
    assert convert_to_primitive('FaLSe') is False
    assert convert_to_primitive('\nFalse\n') is False
    assert convert_to_primitive(False) is False

    assert convert_to_primitive('0') == 0
    assert convert_to_primitive(' 0 ') == 0
    assert convert_to_primitive(0) == 0
    assert isinstance(convert_to_primitive('0'), int)
    assert convert_to_primitive('1') == 1
    assert convert_to_primitive('       1\n') == 1
    assert isinstance(convert_to_primitive('1'), int)
    assert convert_to_primitive('-999') == -999
    assert isinstance(convert_to_primitive('-999'), int)

    assert convert_to_primitive('1.9') == 1.9
    assert convert_to_primitive(1.9) == 1.9
    assert isinstance(convert_to_primitive('1.9'), float)
    assert convert_to_primitive('-49.4') == -49.4
    assert convert_to_primitive('\t-49.4\n') == -49.4
    assert isinstance(convert_to_primitive('-49.4'), float)
    assert convert_to_primitive('2.553e83') == 2.553e83
    assert isinstance(convert_to_primitive('2.553e83'), float)

    assert convert_to_primitive('1.9j') == 1.9j
    assert convert_to_primitive(' 1.9j\t  ') == 1.9j
    assert isinstance(convert_to_primitive('1.9j'), complex)
    assert convert_to_primitive('-3+2.4j') == -3 + 2.4j
    assert isinstance(convert_to_primitive('-3+2.4j'), complex)
    assert convert_to_primitive('1+0j') == 1 + 0j
    assert isinstance(convert_to_primitive('1+0j'), complex)
    assert convert_to_primitive('1.52+2.32e-3j') == complex(1.52, 2.32e-3)
    assert isinstance(convert_to_primitive('1.52e8+2.32e-5j'), complex)
    assert convert_to_primitive(-3.2+2.4j) == complex(-3.2, 2.4)

    assert convert_to_primitive('') == ''
    assert convert_to_primitive(' \t \n ') == ' \t \n '
    assert convert_to_primitive('hello') == 'hello'
    assert convert_to_primitive('hello\tworld\r\n') == 'hello\tworld\r\n'
    assert convert_to_primitive(b'\x00\x00') == b'\x00\x00'
    assert convert_to_primitive('16i') == '16i'
    assert convert_to_primitive('[1,2,3]') == '[1,2,3]'

    assert convert_to_primitive([1, 2, 3]) == [1, 2, 3]
    assert convert_to_primitive({'1': 1}) == {'1': 1}
    assert convert_to_primitive(bytearray([1, 2, 3])) == b'\x01\x02\x03'


def test_convert_to_date():

    # test datetime.date object
    d = datetime.date(2000, 8, 24)
    out = convert_to_date(d)
    assert isinstance(out, datetime.date)
    assert out is d
    assert out.year == 2000
    assert out.month == 8
    assert out.day == 24

    # test datetime.datetime object
    # (this is an important timestamp in the movie Back to the Future)
    d = datetime.datetime(1985, 10, 26, hour=1, minute=21, second=0)
    out = convert_to_date(d)
    assert isinstance(out, datetime.date)
    assert out.year == 1985
    assert out.month == 10
    assert out.day == 26

    # test string object
    out = convert_to_date('2010-3-12')
    assert isinstance(out, datetime.date)
    assert out.year == 2010
    assert out.month == 3
    assert out.day == 12

    # test string with format
    out = convert_to_date('22.6.2100', fmt='%d.%m.%Y')
    assert isinstance(out, datetime.date)
    assert out.year == 2100
    assert out.month == 6
    assert out.day == 22

    # test invalid string with strict=False
    for item in ['2010-13-12', 'xxx', '22.6.2100']:
        out = convert_to_date(item, strict=False)
        assert isinstance(out, datetime.date)
        assert out.year == datetime.MINYEAR
        assert out.month == 1
        assert out.day == 1

        with pytest.raises(ValueError):
            convert_to_date(item, strict=True)

    # test None object
    out = convert_to_date(None)
    assert isinstance(out, datetime.date)
    assert out.year == datetime.MINYEAR
    assert out.month == 1
    assert out.day == 1


def test_convert_to_xml_string():

    root = Element('msl')

    team = Element('team')
    team.text = 'Light'
    root.append(team)

    data = Element('data')
    for a, b in [('one', '1'), ('two', '2'), ('three', '3')]:
        element = Element(a)
        element.text = b
        data.append(element)
    root.append(data)

    lines = convert_to_xml_string(root).splitlines()
    assert lines[0] == '<?xml version="1.0" encoding="utf-8"?>'
    assert lines[1] == '<msl>'
    assert lines[2] == '  <team>Light</team>'
    assert lines[3] == '  <data>'
    assert lines[4] == '    <one>1</one>'
    assert lines[5] == '    <two>2</two>'
    assert lines[6] == '    <three>3</three>'
    assert lines[7] == '  </data>'
    assert lines[8] == '</msl>'


def test_xml_element():

    element = xml_element('tag')
    assert element.tag == 'tag'
    assert element.text is None
    assert element.tail is None
    assert len(element.attrib) == 0

    element = xml_element('tag', text='the text')
    assert element.tag == 'tag'
    assert element.text == 'the text'
    assert element.tail is None
    assert len(element.attrib) == 0

    element = xml_element('tag', tail='the tail')
    assert element.tag == 'tag'
    assert element.text is None
    assert element.tail == 'the tail'
    assert len(element.attrib) == 0

    element = xml_element('tag', text='the text', tail='the tail', one='1', two='2', three='3')
    assert element.tag == 'tag'
    assert element.text == 'the text'
    assert element.tail == 'the tail'
    assert len(element.attrib) == 3
    assert element.attrib['one'] == '1'
    assert element.attrib['two'] == '2'
    assert element.attrib['three'] == '3'


def test_xml_comment():
    element = xml_comment('this is a comment')
    assert element.tag == Comment
    assert element.text == 'this is a comment'


def test_convert_to_xml_string_v2():
    root = xml_element('root')
    housekeeping = xml_element('Housekeeping')

    job = xml_element('job', text='ABC123')

    client = xml_element('client', city='Wellington')
    client.text = 'NZ Mass Inc.'

    masses = xml_element('masses')
    for index, mass in enumerate(['1ug', '1mg', '1g', '1kg']):
        masses.append(xml_element('mass_{}'.format(index), text=mass))

    housekeeping.append(masses)
    housekeeping.append(job)
    housekeeping.append(xml_comment('the Client info'))
    housekeeping.append(client)
    housekeeping.append(xml_element('bug', tail='Bugger'))

    root.append(xml_comment('Here is some information from the Housekeeping GUI'))
    root.append(housekeeping)

    lines = convert_to_xml_string(root).splitlines()
    assert lines[0] == '<?xml version="1.0" encoding="utf-8"?>'
    assert lines[1] == '<root>'
    assert lines[2] == '  <!--Here is some information from the Housekeeping GUI-->'
    assert lines[3] == '  <Housekeeping>'
    assert lines[4] == '    <masses>'
    assert lines[5] == '      <mass_0>1ug</mass_0>'
    assert lines[6] == '      <mass_1>1mg</mass_1>'
    assert lines[7] == '      <mass_2>1g</mass_2>'
    assert lines[8] == '      <mass_3>1kg</mass_3>'
    assert lines[9] == '    </masses>'
    assert lines[10] == '    <job>ABC123</job>'
    assert lines[11] == '    <!--the Client info-->'
    assert lines[12] == '    <client city="Wellington">NZ Mass Inc.</client>'
    assert lines[13] == '    <bug/>'
    assert lines[14] == '    Bugger'
    assert lines[15] == '  </Housekeeping>'
    assert lines[16] == '</root>'
