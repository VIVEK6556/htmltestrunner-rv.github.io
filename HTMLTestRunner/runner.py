# -*- coding: utf-8 -*-
# module runner.py
#
# Copyright (c) 2021-2030  Ravikirana B
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
__doc__ = \
    """
    HTMLTestRunner-rv module to generate HTML report for your testcase
    ==================================================================
    
    The HTMLTestRunner provides easy way to generate HTML Test Reports.
    Easy to find errors and reduce the debug time.
    You no need to see console to see the debug messages, it logs every print logs in to *.txt with timestamp.
    So it is easy to debug whenever you want.
    
    *   It automatically opens report in your browser so no need to search report file in your directory.
        Just you need to pass `open_in_browser = True`.
    
    *   Color of Testcase block automatically change as per test result.
                    
    
    """

__author__ = "Ravikirana B ravikiranb36@gmail.com"
__version__ = "1.0.13"
__all__ = ['HTMLTestRunner']

from datetime import datetime
import os
import re
from io import StringIO
import sys
import time
import unittest
import shutil
from jinja2 import Environment, FileSystemLoader

from pyparsing import unicode


def to_unicode(s):
    """
    It strings to unicode
    Args:
        s (str): String to convert to unicode

    Returns:
        It returns unicode
    """
    try:
        return unicode(s)
    except UnicodeDecodeError:
        # s is non ascii byte string
        return s.decode('utf-8', 'ignore')


class OutputRedirector(object):
    """Wrapper to redirect stdout or stderr"""

    def __init__(self, fp):
        """
        Wrapper to redirect stdout or stderr
        Args:
            fp (buffer): Buffer to store stdout
        """
        self.fp = fp

    def write(self, s):
        """
        Write to string buffer with timestamp
        Args:
            s (str): String to write to buffer

        Returns:
                It returns None
        """
        string = to_unicode(s)
        if string == '\n' or string == ' ':
            pass
        else:
            output = str(datetime.now()) + ' : ' + string.replace('\n', '\n' + ' ' * 29) + '\n'
            self.fp.write(output)

    def writelines(self, lines):
        """
        It write number lines to buffer
        Args:
            lines (list): List of lines to write to buffer

        Returns:

        """
        lines = map(to_unicode, lines)
        self.fp.writelines(lines)

    def flush(self):
        """
        It flushes string buffer
        Returns:

        """
        self.fp.flush()


# stdout redirectord
stdout_redirector = OutputRedirector(sys.stdout)
stderr_redirector = OutputRedirector(sys.stderr)

# Test status
STATUS = {
    0: 'PASS',
    1: 'FAIL',
    2: 'ERROR',
}

DEFAULT_TITLE = 'Unit Test Report'
DEFAULT_DESCRIPTION = 'Test report generation using HTMLTestRunner-rv'

PKG_PATH = os.path.dirname(__file__)
TestResult = unittest.TestResult


class _TestResult(TestResult):

    def __init__(self, verbosity=1, log_file=''):
        """
        It generates test result
        Args:
            verbosity (int): If ``verbosity > 1`` it logs all details
            log_file (file): File name to log the ``stdout`` logs
        """
        TestResult.__init__(self)
        self.log_file = log_file
        self.outputBuffer = StringIO()
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.verbosity = verbosity
        self.result = []

    def startTest(self, test):
        """
        Start test inherited by unittest TestResult.
        It changes stdout buffer to ``self.outputBuffer``
        Args:
            test : Test object to do test

        Returns:

        """
        TestResult.startTest(self, test)
        # just one buffer for both stdout and stderr
        stdout_redirector.fp = self.outputBuffer
        stderr_redirector.fp = self.outputBuffer
        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector

    def complete_output(self):
        """
        It disconnects ``self.outputBuffer`` from ``stdout`` and replaces with ``sys.stdout = sys.__stdout__``,
        ``sys.stderr = sys.__stderr__``
        writes buffer data to log file ``if self.log_file is True``
        Returns:
            It returns buffer ``output``
        """
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        output = self.outputBuffer.getvalue()
        self.outputBuffer.seek(0)
        self.outputBuffer.truncate(0)
        # Writing buffer data to log file
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(output)
        return output

    def stopTest(self, test):
        """
        Calls ``addSuccess()`` if testcase passed.
        Calls ``addError()`` if gets error while testing.
        Calls ``addFailure()`` if test has failed.
        It disconnects ``self.outputBuffer`` from ``stdout`` and replaces with ``sys.__stdout__``
        Args:
            test: Testcase to stop after it runs

        Returns:

        """
        self.complete_output()

    def addSuccess(self, test):
        """
        It override method of ``class unittest.TestResult``
        It writes P in console
        Args:
            test: Testcase

        Returns:

        """
        self.success_count += 1
        TestResult.addSuccess(self, test)
        output = self.complete_output()
        self.result.append((0, test, output, ''))
        if self.verbosity > 1:
            sys.stderr.write('ok ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stdout.write('P')

    def addError(self, test, err):
        """
        It override method of ``class unittest.TestResult``
        It writes E in console
        Args:
            test: Testcase

        Returns:

        """
        self.error_count += 1
        TestResult.addError(self, test, err)
        _, _exc_str = self.errors[-1]
        output = self.complete_output()
        self.result.append((2, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('E')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('E')

    def addFailure(self, test, err):
        """
        It override method of ``class unittest.TestResult``
        It writes F in console
        Args:
            test: TestCase

        Returns:

        """
        self.failure_count += 1
        TestResult.addFailure(self, test, err)
        _, _exc_str = self.failures[-1]
        output = self.complete_output()
        self.result.append((1, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('F  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('F')


class HTMLTestRunner:
    def __init__(self, log=None, output=None, verbosity=1, title=None, description=None, report_name='report',
                 open_in_browser=False):
        """
        HTMLTestRunner
        Args:
            self (HTMLTestRunner): Object of HTMLTestRunner
            log (bool): If ``True`` it logs print buffer to *.txt file with timestamp
            output (str): Report output dir name
            verbosity (int): If ``verbosity > 1`` it prints brief summary of testcases in console
            title (str): Title of the Test Report
            description (str): Description of Test Report
            report_name (str): Starting name of Test report and log file
            open_in_browser (bool): If ``True`` it opens report in browser automatically

        Returns:
            Runner object
        """
        self.report_name = report_name
        self.output = output
        if self.output is None:
            self.output = 'reports'
        self.open_in_browser = open_in_browser
        self.html_report_file_name = f'./{self.output}/{self.report_name}_{time.strftime("%d-%m-%y %I-%M-%S")}.html'
        os.makedirs(os.path.dirname(self.html_report_file_name), exist_ok=True)
        self.log_file = ''
        if log:
            self.log_file = f'./{self.output}/{self.report_name}_{time.strftime("%d-%m-%y %I-%M-%S")}_log.txt'
        self.verbosity = verbosity
        if title is None:
            self.title = DEFAULT_TITLE
        else:
            self.title = title
        if description is None:
            self.description = DEFAULT_DESCRIPTION
        else:
            self.description = description

        self.startTime = datetime.now()

    def run(self, test):
        """
        Run the Test Case
        Args:
            test: Test Case

        Returns:
            It returns ``result``
        """
        result = _TestResult(self.verbosity, self.log_file)
        test(result)
        self.stopTime = datetime.now()
        self.generateReport(result)
        return result

    def sortResult(self, result_list):
        """
        It sorts the Testcases to run
        Args:
            result_list (list): Results list

        Returns:
            Returns sorted result list
        """
        rmap = {}
        classes = []
        for n, t, o, e in result_list:
            cls = t.__class__
            if not cls in rmap:
                rmap[cls] = []
                classes.append(cls)
            rmap[cls].append((n, t, o, e))
        r = [(cls, rmap[cls]) for cls in classes]
        return r

    def getReportAttributes(self, result):
        """
        Return report attributes as a list of (name, value).
        Override this to add custom attributes.
        """
        startTime = str(self.startTime)[:19]
        duration = str(self.stopTime - self.startTime)
        status = []
        if result.success_count: status.append('Pass %s' % result.success_count)
        if result.failure_count: status.append('Failure %s' % result.failure_count)
        if result.error_count:   status.append('Error %s' % result.error_count)
        if status:
            status = ' '.join(status)
        else:
            status = 'none'
        return [
            ('Start Time', startTime),
            ('Duration', duration),
            ('Status', status),
            ('Descrition', self.description)
        ]

    def generateReport(self, result):
        """
        It geneartes HTML report by using unittest report
        @param result:unittest result
        After generates html report it opens report in browser if open_in_broser is True
        It adds stylesheet and script files in reports directory
        """
        report_attrs = self.getReportAttributes(result)
        generator = 'HTMLTestRunner %s' % __version__
        report = self._generate_report(result)
        env = Environment(loader=FileSystemLoader(os.path.join(PKG_PATH, 'templates')))
        template = env.get_template('template.html')
        output = template.render(
            generator=generator,
            report_attrs=report_attrs,
            title=self.title,
            report=report,
            stop_time=(self.stopTime - self.startTime),
        )

        shutil.copy(os.path.join(PKG_PATH, 'static', 'stylesheet.css'), f'./{self.output}/stylesheet.css')
        shutil.copy(os.path.join(PKG_PATH, 'static', 'script.js'), f'./{self.output}/script.js')
        with open(self.html_report_file_name, 'w') as file:
            file.write(output)
        if self.open_in_browser:
            import webbrowser
            webbrowser.open_new_tab('file:///' + os.getcwd() + self.html_report_file_name)

    def _generate_report(self, result):
        """
        Generates report
        Args:
            result: Test Result

        Returns :
            Returns Test Report dictionary
            ``report = {
            'class_testcases': class_testcases,
            'count': str(result.success_count + result.failure_count + result.error_count),
            'pass': str(result.success_count),
            'fail': str(result.failure_count),
            'error': str(result.error_count),
        }``
        """
        class_testcases = []
        sortedResult = self.sortResult(result.result)
        for cid, (cls, cls_results) in enumerate(sortedResult):
            # subtotal for a class
            np = nf = ne = 0
            for n, t, o, e in cls_results:
                if n == 0:
                    np += 1
                elif n == 1:
                    nf += 1
                else:
                    ne += 1

            # format class description
            if cls.__module__ == "__main__":
                name = cls.__name__
            else:
                name = "%s.%s" % (cls.__module__, cls.__name__)
            doc = cls.__doc__ and cls.__doc__.split("\n")[0] or ""
            desc = doc and '%s: %s' % (name, doc) or name

            fun_testcases = []
            for tid, (n, t, o, e) in enumerate(cls_results):
                self._generate_report_test(fun_testcases, cid, tid, n, t, o, e)
            cls_testcase = {
                'style': ne > 0 and 'errorClass' or nf > 0 and 'failClass' or 'passClass',
                'desc': desc,
                'count': np + nf + ne,
                'pass': np,
                'fail': nf,
                'error': ne,
                'cid': 'c%s' % (cid + 1),
                'fun_testcases': fun_testcases,
            }
            class_testcases.append(cls_testcase)
        report = {
            'class_testcases': class_testcases,
            'count': str(result.success_count + result.failure_count + result.error_count),
            'pass': str(result.success_count),
            'fail': str(result.failure_count),
            'error': str(result.error_count),
        }
        return report

    def _generate_report_test(self, fun_testcases, cid, tid, n, t, o, e):
        """
        It appends result to ``fun_testcases``
        Args:
            fun_testcases (list): testcase function result list

        Returns:

        """
        # e.g. 'pt1.1', 'ft1.1', etc
        has_output = bool(o or e)
        if not has_output:
            return
        tid = (n == 0 and 'p' or 'f') + 't%s.%s' % (cid + 1, tid + 1)
        name = t.id().split('.')[-1]
        doc = t.shortDescription() or ""
        desc = doc and ('%s: %s' % (name, doc)) or name

        # o and e should be byte string because they are collected from stdout and stderr?
        if not isinstance(o, str):
            uo = o.decode('utf-8', 'ignore')
        else:
            uo = o
        if not isinstance(e, str):
            ue = e.decode('utf-8', 'ignore')
        else:
            ue = e

        log = uo
        error = ue
        testcase = {
            'tid': tid,
            'class': (n == 0 and 'hiddenRow' or 'none'),
            'style': n == 2 and 'errorCase' or (n == 1 and 'failCase' or 'passCase'),
            'desc': desc,
            'log': re.sub('\x00', '', log),
            'error': error,
            'status': STATUS[n],
        }
        fun_testcases.append(testcase)
