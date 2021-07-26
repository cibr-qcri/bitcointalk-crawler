from hashlib import sha256


class BitcoinTalkHelper:

    @staticmethod
    def decode_base58(bc, length):
        digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        n = 0
        for char in bc:
            n = n * 58 + digits58.index(char)
        return n.to_bytes(length, 'big')

    def check_bc(self, bc):
        try:
            bcbytes = self.decode_base58(bc, 25)
            return bcbytes[-4:] == sha256(sha256(
                bcbytes[:-4]).digest()).digest()[:4]
        except:
            return False
