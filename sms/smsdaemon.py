#!/usr/bin/env python
# coding: utf-8
'''
.. moduleauthor:: Genilson Israel da Silva <genilsonisrael@gmail.com>

:Platform: \*nix

:Synopsis: This module implements the Daemon funcionalities extended from
    :class:`Daemon` that keeps waiting for an incoming callback event.

Code
------
'''

import gammu
import sys
import datetime
import time
from re import findall
from daemon import Daemon
from settings import *
from subprocess import Popen, PIPE
from os import fdopen
from serial import Serial


#Configuring up the daemon
class SMSD(Daemon):

    '''Creates a daemon that listens to incoming phone notifications.
    Extends Daemon

    :param pidfile: file to keep pid
    :type pidfile: str
    :param stdin: path to stdin file
    :type stdin: str
    :param stdout: pato to stdout file
    :type stdout: str
    :param stderr: path to stderr file
    :type stderr: str

    '''

    #SMSCs of major phone carriers in Brazil
    SMSCs = {
        'TIM': '+5511831382000',
        'OI': '+550310000010',
        'CLARO': '+553184015300',
        'VIVO': '+550101102010',
    }

    def callback(self, sm, type_event, data):
        '''This callback receives notification about incoming SMSes,
        processeses and replies them with the execution status

        :param sm: state machine which invoked action
        :type sm: :class: `gammu.StateMachine` object
        :param type_event: type of action, SMS is the one that matters
        :type type_event: string, incoming type
        :param data: event data
        :type data: dict with sms info

        '''
        # Folder and location of SMS in storage
        f, l = data['Folder'], data['Location']
        data = sm.GetSMS(f, l)[0]
        # Deleting SMS so SIM storage won't run out of space
        sm.DeleteSMS(f, l)
        # Verifying if the phone is allowed to execute operations
        if not data['Number'] in ALLOWED_PHONES:
            sys.stderr.write('Err: Phone not allowed to run commands: %s\n' %
                             data['Number'])
        elif type_event != 'SMS':
            sys.stderr.write('Err: Incoming event notification not '
                             'supported\n')
        else:
            sys.stdout.write('Incoming %s event notification received.\n' %
                             type_event)
            # Logging operation
            sys.stdout.write(
                'Phone: {}\n'
                'Received in: {}\n'
                'Operation (Length: {}): {}\n'.format(
                    data['Number'],
                    data['DateTime'].strftime('%d/%m/%Y at %Hh%Mmin%Sseg'),
                    data['Length'], data['Text']))

            saida = self.run_cmd(data['Text'].lower())
            self.send_sms(sm, saida, data['Number'])

    # Reads serial output
    def serial_read(self, s):
        '''Reads from serial after input

        :param s: serial connection
        :type s: :class: `serial.serialposix.Serial` object
        :returns: phone answer after input

        '''

        ol = []
        while 1:
            c = s.read()
            if not c:
                break
            ol.append(c)
        return ''.join(ol)

    def run_cmd(self, cmd):
        '''Runs cmd in the system  host

        :param sm: state machine which invoked action
        :type sm: :class: `gammu.StateMachine` object
        :returns: stderr of command (if errors occurred) or stdout (up to 160
        characters or default execution success message instead)

        '''

        process = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                        close_fds=True)
        out, err = process.stdout.read(), process.stderr.read()

        if len(err) > 0:
            # Logging error
            sys.stderr.write('Erro: %s\n' % err)
            return err
        elif 0 < len(out) <= 160:
            return out
        return 'Comando executado com sucesso.\nSaida muito longa para envio.'

    def send_sms(self, sm, msg, dest):
        '''Sends sms to phone through :meth:`gammu.StateMachine.SendSMS`

        :param sm: state machine which invoked action
        :type sm: :class: `gammu.StateMachine` object
        :param msg: message to be sent
        :type msg: string

        '''

        # GSM Operator
        oper = gammu.GSMNetworks[sm.GetNetworkInfo()['NetworkCode']].upper()

        # SMSC configuration
        smsc_cfg = {
            'Name': oper,
            'Number': self.SMSCs[oper],
            'Validity': '1H',
        }

        # Message structure
        message = {
            'SMSC': smsc_cfg,
            'Name': 'Gammu Reply',
            'Text': msg,
            'Number': dest,
        }

        # Acutally send SMS message
        sm.SendSMS(message)

    def run(self):
        '''
        Uses :mod:`gammu` to interact with the phone. Configures incoming
        callback notifications and waits for notifications from phone.

        '''

        #Sets stdout buffer to zero
        sys.stdout = fdopen(sys.stdout.fileno(), 'w', 0)
        ser = Serial(PORT, TRANSF, timeout=3)
        # Setting the SIM card as default storage for SMSes
        ser.write('AT+CPMS="SM","SM","SM"\r')
        answ = findall(r'(?:.*\r\n(.+)\r\n)$', self.serial_read(ser))[0]
        if answ == "ERROR":
            sys.stderr.write('Err: SIM storage not supported by phone\n')
            sys.exit(2)

        ser.close()
        # Create state machine
        sm = gammu.StateMachine()
        # Creates .gammurc file
        open('.gammurc', 'w').write('[gammu]\n'
                                    'port={}\n'
                                    'connection={}\n'
                                    'name={}'.format(PORT, CON, NAME))
        # Read gammurc (.gammurc)
        sm.ReadConfig(Filename='.gammurc')
        # Initialize state machine and connect to phone
        sm.Init()
        # Set callback handler for incoming notifications
        sm.SetIncomingCallback(self.callback)

        # Enable notifications from incoming SMS.
        try:
            sm.SetIncomingSMS()
        except gammu.ERR_NOTSUPPORTED:
            sys.stderr.write('Err: Incomming SMS notification not supported '
                             'by phone\n')
            sys.exit(2)

        # Keeps communicating with the phone in order to get notification
        while 1:
            sm.GetSignalQuality()
            time.sleep(1)
